import json
import traceback

from sqlalchemy import MetaData
from llama_index.objects import SQLTableSchema
from langchain.chat_models import ChatOpenAI
from llama_index import SQLDatabase

from sql_metadata import Parser
from langchain.chains import LLMChain
import re

from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate, SystemMessagePromptTemplate,
)

from config.settings.base import OPEN_API_TOKEN, AGENT_LLM_MODEL_EVAL
from src.db.utils import CustomJSONEncoder

SYSTEM_TEMPLATE = """You are a {dialect} expert.
Given a question, a SQL query, and the database schema, analyze the correctness of the SQL query and provide a score.
Score indicates how correctly and accurately SQL query answers the question.
Note that the score should be between 0 and 100. Higher scores means the SQL Query is more accurate.
Double check the SQL query for the common mistakes, including:
- For columns that can contain NULL values, NULL values should be filtered out by using the IS NOT NULL operator in the WHERE condition
- when intention of the question is to include all rows from both sets, including duplicates, using UNION ALL is better than UNION
- BETWEEN is inclusive, if the intention is to exclude the endpoints of the range, use comparison operators (< and >)
- Conditions in the WHERE clause should not have any DATA TYPE mismatch problem
- columns names which contain Spaces, non-alphanumeric character, Reserved keywords or special characters should be inside backticks (``)
- Using the correct number of arguments for functions
- Casting to the correct data type
- Using the proper columns for joins
- using the correct set operators for nested queries
- columns in the SELECT clause should correspond to what exactly asked by user in the question
- check for the improper use of the aggregation functions (SUM, AVG, MIN, MAX, ...)
- robustness of the SQL query in handling cases where data values can be in different format (WHERE lower(column) = lower(entity))
"""

HUMAN_TEMPLATE = """
Give me a score for the SQL query.
Schema of the tables:
{schema}
Here is the question:
Question: {question}
Evaluate the following SQL query:
SQL Query: {SQL}
SQL Query Result: {SQL_result}
give me a one or two lines explanation and the score after 'Score: '.
"""


def answer_parser_simple(answer: str) -> int:
    """
    Extract the number after the Score:
    If not found extract the last number between 0 and 100
    If not found return 0
    """
    pattern = r".*Score:\s*(\d+)"
    match = re.search(pattern, answer)
    output = 0
    if match:
        output = int(match.group(1))
    else:
        pattern = r"\b([0-9]{1,2}|100)\b"
        numbers = re.findall(pattern, answer)
        if numbers:
            output = int(numbers[-1])
    return output


def evaluate_sql_query_simple(text_query, generated_sql, engine, formatted_result):
    try:
        if generated_sql is None:
            return 0

        metadata_obj = MetaData()
        metadata_obj.reflect(engine)
        llm = ChatOpenAI(model_name=AGENT_LLM_MODEL_EVAL, openai_api_key=OPEN_API_TOKEN)
        table_schema_objs = [SQLTableSchema(table_name=table_name) for table_name in metadata_obj.tables.keys()]
        database = SQLDatabase(engine=engine)
        system_message_prompt = SystemMessagePromptTemplate.from_template(
            SYSTEM_TEMPLATE
        )

        human_message_prompt = HumanMessagePromptTemplate.from_template(HUMAN_TEMPLATE)
        chat_prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )
        dialect = database.dialect
        tables = Parser(generated_sql).tables
        schema = ""
        for scanned_table in table_schema_objs:
            if scanned_table.table_name in tables:
                schema += f"Table: {scanned_table.table_name}\n"
        chain = LLMChain(llm=llm, prompt=chat_prompt)
        answer = chain.run(
            {
                "dialect": dialect,
                "question": text_query,
                "SQL": generated_sql,
                "SQL_result": json.dumps(formatted_result, separators=(',', ':'), cls=CustomJSONEncoder),
                "schema": schema,
            }
        )
        # TODO: get total_tokens and total_cost
        score = answer_parser_simple(answer=answer) / 100
    except Exception as e:
        print(f"evaluate_sql_query_simple, cant execute LLMChain query, e={e}")
        traceback.print_exc()
        return 0

    print(f"evaluate_sql_query_simple, score={score}")
    return score
