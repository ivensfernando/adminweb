"""Toolkit for interacting with an SQL database."""
from typing import List

from langchain_core.pydantic_v1 import Field
from langchain.embeddings import OpenAIEmbeddings

from langchain.agents.agent_toolkits.base import BaseToolkit
from langchain.tools import BaseTool

from src.query_engine.langchain.tools.sql_database.tool import (
    QuerySQLDataBaseTool,
)
from src.query_engine.langchain.tools.sql_database.experimental.tool import GetAdminInstructions, SystemTime, \
    TablesSQLDatabaseTool, SchemaSQLDatabaseTool, InfoRelevantColumns, ColumnEntityChecker, GetFewShotExamples
from src.query_engine.langchain.utilities.sql_database import SQLDatabase


class SQLDatabaseToolkit(BaseToolkit):
    """Dataherald toolkit"""

    db: SQLDatabase = Field(exclude=True)
    context: List[dict] | None = Field(exclude=True, default=None)
    few_shot_examples: List[dict] | None = Field(exclude=True, default=None)
    security_instructions: List[dict] | None = Field(exclude=True, default=None)
    db_scan: List = Field(exclude=True)
    embedding: OpenAIEmbeddings = Field(exclude=True)

    @property
    def dialect(self) -> str:
        """Return string representation of SQL dialect to use."""
        return self.db.dialect

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    def get_tools(self) -> List[BaseTool]:
        """Get the tools in the toolkit."""
        tools = []
        query_sql_db_tool = QuerySQLDataBaseTool(db=self.db, context=self.context)
        tools.append(query_sql_db_tool)
        if self.security_instructions is not None:
            tools.append(
                GetAdminInstructions(
                    db=self.db, context=self.context, security_instructions=self.security_instructions
                )
            )
        get_current_datetime = SystemTime(db=self.db, context=self.context)
        tools.append(get_current_datetime)
        tables_sql_db_tool = TablesSQLDatabaseTool(
            db=self.db,
            context=self.context,
            db_scan=self.db_scan,
            embedding=self.embedding,
        )
        tools.append(tables_sql_db_tool)
        schema_sql_db_tool = SchemaSQLDatabaseTool(
            db=self.db, context=self.context, db_scan=self.db_scan
        )
        tools.append(schema_sql_db_tool)
        info_relevant_tool = InfoRelevantColumns(
            db=self.db, context=self.context, db_scan=self.db_scan
        )
        tools.append(info_relevant_tool)
        column_sample_tool = ColumnEntityChecker(db=self.db, context=self.context)
        tools.append(column_sample_tool)
        if self.context is not None:
            context = self.context
            if self.few_shot_examples is not None and len(self.few_shot_examples) > 0:
                context.append(self.few_shot_examples)
            get_fewshot_examples_tool = GetFewShotExamples(
                db=self.db,
                context=context,
            )
            tools.append(get_fewshot_examples_tool)
        return tools
