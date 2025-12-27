import datetime
import difflib
import logging
import os
from functools import wraps
from typing import Any, Callable, List

import numpy as np
import openai
import pandas as pd
import sqlalchemy
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.embeddings import OpenAIEmbeddings
from langchain.tools.base import BaseTool
from pydantic import BaseModel, Field
from sqlalchemy import MetaData
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import func

from src.query_engine.langchain.agents.agent_toolkits.experimental.sql_database import \
    SQLDatabase as SQLDatabaseExperimental

logger = logging.getLogger(__name__)

TOP_K = int(os.getenv("UPPER_LIMIT_QUERY_RETURN_ROWS", "50"))
EMBEDDING_MODEL = "text-embedding-ada-002"


def catch_exceptions():  # noqa: C901
    def decorator(fn: Callable[[str], str]) -> Callable[[str], str]:  # noqa: C901
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:  # noqa: PLR0911
            try:
                return fn(*args, **kwargs)
            except openai.error.APIError as e:
                # Handle API error here, e.g. retry or log
                return f"OpenAI API returned an API Error: {e}"
            except openai.error.APIConnectionError as e:
                # Handle connection error here
                return f"Failed to connect to OpenAI API: {e}"
            except openai.error.RateLimitError as e:
                # Handle rate limit error (we recommend using exponential backoff)
                return f"OpenAI API request exceeded rate limit: {e}"
            except openai.error.Timeout as e:
                # Handle timeout error (we recommend using exponential backoff)
                return f"OpenAI API request timed out: {e}"
            except openai.error.ServiceUnavailableError as e:
                # Handle service unavailable error (we recommend using exponential backoff)
                return f"OpenAI API service unavailable: {e}"
            except openai.error.InvalidRequestError as e:
                return f"OpenAI API request was invalid: {e}"
            except SQLAlchemyError as e:
                return f"Error: SQLAlchemyError, {e}"
            except Exception as e:
                return f"Error: Exception, {e}"

        return wrapper

    return decorator


# Classes needed for tools
class BaseSQLDatabaseTool(BaseModel):
    """Base tool for interacting with the SQL database and the context information."""

    db: SQLDatabaseExperimental = Field(exclude=True)
    context: List[dict] | None = Field(exclude=True, default=None)

    class Config(BaseTool.Config):
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True
        extra = "allow"


class SystemTime(BaseSQLDatabaseTool, BaseTool):
    """Tool for finding the current data and time."""

    name = "system_time"
    description = """
    Input is an empty string, output is the current data and time.
    Always use this tool before generating a query if there is any time or date in the given question.
    """

    @catch_exceptions()
    def _run(
            self,
            tool_input: str = "",  # noqa: ARG002
            run_manager: CallbackManagerForToolRun | None = None,  # noqa: ARG002
    ) -> str:
        """Execute the query, return the results or an error message."""
        current_datetime = datetime.datetime.now()
        return f"Current Date and Time: {str(current_datetime)}"

    async def _arun(
            self,
            tool_input: str,
            run_manager: AsyncCallbackManagerForToolRun | None = None,
    ) -> str:
        return self._run(tool_input, run_manager)


class QuerySQLDataBaseTool(BaseSQLDatabaseTool, BaseTool):
    """Tool for querying a SQL database."""

    name = "sql_db_query"
    description = """
    Input: SQL query.
    Output: Result from the database or an error message if the query is incorrect.
    If an error occurs, rewrite the query and retry.
    Use this tool to execute SQL queries.
    """

    @catch_exceptions()
    def _run(
            self,
            query: str,
            top_k: int = TOP_K,
            run_manager: CallbackManagerForToolRun | None = None,  # noqa: ARG002
    ) -> str:
        """Execute the query, return the results or an error message."""
        if "```sql" in query:
            logger.info("**** Removing markdown formatting from the query\n")
            query = query.replace("```sql", "").replace("```", "")
            logger.info(f"**** Query after removing markdown formatting: {query}\n")
        return self.db.run_sql(query, top_k=top_k)[0]

    async def _arun(
            self,
            query: str,
            run_manager: AsyncCallbackManagerForToolRun | None = None,
    ) -> str:
        return self._run(query, run_manager)


class GetAdminInstructions(BaseSQLDatabaseTool, BaseTool):
    """Tool for retrieving the instructions from the user"""

    name = "get_admin_instructions"
    description = """
    Input: is an empty string.
    Output: Database admin instructions before generating the SQL query.
    The generated SQL query MUST follow the admin instructions even it contradicts with the given question.
    """
    security_instructions: List[dict]

    @catch_exceptions()
    def _run(
            self,
            tool_input: str = "",  # noqa: ARG002
            run_manager: CallbackManagerForToolRun | None = None,  # noqa: ARG002
    ) -> str:
        response = "Admin: All of the generated SQL queries must NOT use prohibited columns/table. See the instructions below:\n"
        response += "You should not select columns that have access prohibited. Do not build SQL with any column in combination with table. This is the format: Column:column_name_example - Table:table_name_example"
        for instruction in self.security_instructions:
            table_column = instruction["table_column"]
            access_type = instruction["access_type"]
            table_name = instruction["table_name"]
            print(
                f"GetAdminInstructions, table_column={table_column}, access_type={access_type}, table_name={table_name}")
            if access_type == 1:
                response += f"Column:'{table_column}' - Table:'{table_name}'\n"
        return response

    async def _arun(
            self,
            tool_input: str,
            run_manager: AsyncCallbackManagerForToolRun | None = None,
    ) -> str:
        return self._run(tool_input, run_manager)


class TablesSQLDatabaseTool(BaseSQLDatabaseTool, BaseTool):
    """Tool which takes in the given question and returns a list of tables with their relevance score to the question"""

    name = "db_tables_with_relevance_scores"
    description = """
    Input: Given question.
    Output: Comma-separated list of tables with their relevance scores, indicating their relevance to the question.
    Use this tool to identify the relevant tables for the given question.
    """
    db_scan: List
    embedding: OpenAIEmbeddings

    def get_embedding(
            self,
            text: str,
    ) -> List[float]:
        text = text.replace("\n", " ")
        return self.embedding.embed_query(text)

    def cosine_similarity(self, a: List[float], b: List[float]) -> float:
        return round(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)), 4)

    @catch_exceptions()
    def _run(
            self,
            user_question: str,
            run_manager: CallbackManagerForToolRun | None = None,  # noqa: ARG002
    ) -> str:
        """Use the concatenation of table name, columns names, and the description of the table as the table representation"""
        question_embedding = self.get_embedding(user_question)
        table_representations = []
        for table in self.db_scan:
            col_rep = ""
            for column in table["table_columns"]:
                col_rep += column["name"] + " "
            table_name = table["table_name"]
            selected_table_columns = table["table_columns"]
            foreign_keys = table["foreign_keys"]
            examples = table["examples"]
            filtered_columns = [column for column in selected_table_columns if '_airbyte' not in column["name"]]

            table_rep = f"""-- Table={table_name}, columns={filtered_columns}, foreign_keys={foreign_keys}, examples={examples}. """
            table_representations.append([table["table_name"], table_rep])
        df = pd.DataFrame(
            table_representations, columns=["table_name", "table_representation"]
        )
        df["table_embedding"] = df.table_representation.apply(
            lambda x: self.get_embedding(x)
        )
        df["similarities"] = df.table_embedding.apply(
            lambda x: self.cosine_similarity(x, question_embedding)
        )
        table_relevance = ""
        for _, row in df.iterrows():
            table_relevance += (
                f'Table: {row["table_name"]}, relevance score: {row["similarities"]}\n'
            )
        return table_relevance

    async def _arun(
            self,
            user_question: str,
            run_manager: AsyncCallbackManagerForToolRun | None = None,
    ) -> str:
        return self._run(user_question, run_manager)


class ColumnEntityChecker(BaseSQLDatabaseTool, BaseTool):
    """Tool for checking the existance of an entity inside a column."""

    name = "db_column_entity_checker"
    description = """
    Input: Column name and its corresponding table, and an entity.
    Output: cell-values found in the column similar to the given entity.
    Use this tool to get cell values similar to the given entity in the given column.

    Example Input: table1 -> column2, entity
    """

    def find_similar_strings(
            self, input_list: List[tuple], target_string: str, threshold=0.4
    ):
        similar_strings = []
        for item in input_list:
            similarity = difflib.SequenceMatcher(
                None, str(item[0]).strip().lower(), target_string.lower()
            ).ratio()
            if similarity >= threshold:
                similar_strings.append((str(item[0]).strip(), similarity))
        similar_strings.sort(key=lambda x: x[1], reverse=True)
        return similar_strings[:25]

    @catch_exceptions()
    def _run(
            self,
            tool_input: str,
            run_manager: CallbackManagerForToolRun | None = None,  # noqa: ARG002
    ) -> str:
        try:
            schema, entity = tool_input.split(",")
            table_name, column_name = schema.split("->")
        except ValueError:
            return "Invalid input format, use following format: table_name -> column_name, entity (entity should be a string without ',')"
        search_pattern = f"%{entity.strip().lower()}%"
        meta = MetaData(bind=self.db.engine)
        table = sqlalchemy.Table(table_name.strip(), meta, autoload=True)
        try:
            search_query = sqlalchemy.select(
                [func.distinct(table.c[column_name.strip()])]
            ).where(func.lower(table.c[column_name.strip()]).like(search_pattern))
            search_results = self.db.engine.execute(search_query).fetchall()
            search_results = search_results[:25]
        except SQLAlchemyError:
            search_results = []
        distinct_query = sqlalchemy.select(
            [func.distinct(table.c[column_name.strip()])]
        )
        results = self.db.engine.execute(distinct_query).fetchall()
        results = self.find_similar_strings(results, entity)
        similar_items = "Similar items:\n"
        already_added = {}
        for item in results:
            similar_items += f"{item[0]}\n"
            already_added[item[0]] = True
        if len(search_results) > 0:
            for item in search_results:
                if item[0] not in already_added:
                    similar_items += f"{item[0]}\n"
        return similar_items

    async def _arun(
            self,
            tool_input: str,
            run_manager: AsyncCallbackManagerForToolRun | None = None,
    ) -> str:
        return self._run(tool_input, run_manager)


class SchemaSQLDatabaseTool(BaseSQLDatabaseTool, BaseTool):
    """Tool for getting schema of relevant tables."""

    name = "db_relevant_tables_schema"
    description = """
    Input: Comma-separated list of tables.
    Output: Schema of the specified tables.
    Use this tool to discover all columns of the relevant tables and identify potentially relevant columns.

    Example Input: table1, table2, table3
    """
    db_scan: List

    @catch_exceptions()
    def _run(
            self,
            table_names: str,
            run_manager: CallbackManagerForToolRun | None = None,  # noqa: ARG002
    ) -> str:
        """Get the schema for tables in a comma-separated list."""
        table_names_list = table_names.split(", ")
        tables_schema = ""
        for table in self.db_scan:
            if table["table_name"] in table_names_list:
                table_schema = table["table_schema"] or ""
                tables_schema += table_schema + "\n"
                if table["description"] is not None:
                    tables_schema += "Table description: " + table["description"] + "\n"
        if tables_schema == "":
            tables_schema += "Tables not found in the database"
        return tables_schema

    async def _arun(
            self,
            table_name: str,
            run_manager: AsyncCallbackManagerForToolRun | None = None,
    ) -> str:
        return self._run(table_name, run_manager)


class InfoRelevantColumns(BaseSQLDatabaseTool, BaseTool):
    """Tool for getting more information for potentially relevant columns"""

    name = "db_relevant_columns_info"
    description = """
    Input: Comma-separated list of potentially relevant columns with their corresponding table.
    Output: Information about the values inside the columns and their descriptions.
    Use this tool to gather details about potentially relevant columns. then, filter them, and identify the relevant ones.

    Example Input: table1 -> column1, table1 -> column2, table2 -> column1
    """
    db_scan: List

    @catch_exceptions()
    def _run(
            self,
            column_names: str,
            run_manager: CallbackManagerForToolRun | None = None,  # noqa: ARG002
    ) -> str:
        """Get the column level information."""
        items_list = column_names.split(", ")
        column_full_info = ""
        for item in items_list:
            try:
                table_name, column_name = item.split(" -> ")
            except ValueError:
                # print(f"InfoRelevantColumns, Failed to split, item={item}")
                table_name, column_name = "", ""
                pass
            found = False
            for table in self.db_scan:
                if table_name == table["table_name"]:
                    column_description_list = table.get("column_description_list", "")
                    col_info = ""
                    for column in table["table_columns"]:
                        if column_name == column["name"]:
                            found = True

                            if column_description_list and len(column_description_list) > 0:
                                for c in column_description_list:
                                    if c["column_name"] == column_name:
                                        description = c.get("column_description", "")
                                        if description and len(description) > 0:
                                            col_info += f"Description={description},"

                                        categories = c.get("column_distinct", "")
                                        if categories and len(categories) > 0:
                                            col_info += f"Categories={categories},"
                    col_info += " Sample rows: "
                    if found:
                        for row in table["examples"]:
                            col_info += row[column_name] + ", "
                        col_info = col_info[:-2]
                        column_full_info += f"Table: {table_name}, column: {column_name}, additional info: {col_info}\n"
            if not found:
                column_full_info += f"Table: {table_name}, column: {column_name} not found in database\n"

        print(f"InfoRelevantColumns, end, column_full_info={column_full_info}")
        return column_full_info

    async def _arun(
            self,
            table_name: str,
            run_manager: AsyncCallbackManagerForToolRun | None = None,
    ) -> str:
        return self._run(table_name, run_manager)


class GetFewShotExamples(BaseSQLDatabaseTool, BaseTool):
    """Tool to obtain few-shot examples from the pool of samples"""

    name = "fewshot_examples_retriever"
    description = """
    Input: Number of required Question/SQL pairs.
    Output: List of similar Question/SQL pairs related to the given question.
    Use this tool to fetch previously asked Question/SQL pairs as examples for improving SQL query generation.
    For complex questions, request more examples to gain a better understanding of tables and columns and the SQL keywords to use.
    If the given question is very similar to one of the retrieved examples, it is recommended to use the same SQL query and modify it slightly to fit the given question.
    Always use this tool first and before any other tool!
    """  # noqa: E501
    context: List[dict]

    @catch_exceptions()
    def _run(
            self,
            number_of_samples: str,
            run_manager: CallbackManagerForToolRun | None = None,  # noqa: ARG002
    ) -> str:

        returned_output = ""
        for example in self.context:
            if "used" not in example:
                returned_output += f"Question: {example['question']} -> SQL: {example['answer']}\n"
                example["used"] = True
        if returned_output == "":
            returned_output = "No previously asked Question/SQL pairs are available"
        return returned_output

    async def _arun(
            self,
            number_of_samples: str,
            run_manager: AsyncCallbackManagerForToolRun | None = None,
    ) -> str:
        return self._run(number_of_samples, run_manager)
