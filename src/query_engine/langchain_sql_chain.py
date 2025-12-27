import time
from typing import List

from sqlalchemy.engine import Engine
from langchain.chat_models import ChatOpenAI
from config.settings.base import OPEN_API_TOKEN, AGENT_LLM_MODEL, TEMPERATURE, LANGCHAIN_VERBOSE
from langchain.callbacks import get_openai_callback
from langchain_experimental.sql import SQLDatabaseChain
from langchain.sql_database import SQLDatabase as LangchainSQLDatabase
# from langchain.globals import set_llm_cache
#
# from langchain.cache import RedisSemanticCache
# from langchain.embeddings import OpenAIEmbeddings

from src.db.utils import get_dialect_name
from src.query_engine.langchain_sql_agent import format_intermediate_representations
from src.query_engine.utils import extract_sql_query
import sqlparse
import re

PROMPT_WITHOUT_CONTEXT = """
Given an input question,
first create a syntactically correct {db_dialect} query to run,
then look at the results of the query and return the answer.
Do not give invalid SQL queries. 

The question:
{user_question}
"""

PROMPT_WITH_CONTEXT = """
Given an input question,
first create a syntactically correct {db_dialect} query to run,
then look at the results of the query and return the answer.
Do not give invalid SQL queries. 

An example of a similar question and the query that was generated to answer it is the following
{context}

The question:
{user_question}
"""




def generate_query_with_langchain_sql_chain(
        question: str,
        db_type: str,
        engine: Engine = None,
        context: List[dict] = None,
        db_schema=None,
        ai_model=AGENT_LLM_MODEL,
        ai_temp=TEMPERATURE,
):
    db_dialect = get_dialect_name(db_type)

    llm = ChatOpenAI(model_name=ai_model, openai_api_key=OPEN_API_TOKEN, temperature=ai_temp)
    # llm.cache = True
    #
    # set_llm_cache(RedisSemanticCache(
    #     redis_url="redis://localhost:6379",
    #     embedding=OpenAIEmbeddings()
    # ))

    start_time = time.time()
    if context is not None:
        samples_prompt_string = "The following are some similar previous questions and their correct SQL queries from these databases: \
                \n"
        for sample in context:
            samples_prompt_string += (
                f"Question: {sample['question']} \nSQL: {sample['answer']} \n"
            )

        question_with_context = PROMPT_WITH_CONTEXT.format(
            user_question=question, context=samples_prompt_string, db_dialect=db_dialect
        )
    else:
        question_with_context = PROMPT_WITHOUT_CONTEXT.format(user_question=question, db_dialect=db_dialect)

    # should top_k be an argument?
    db_chain = SQLDatabaseChain.from_llm(
        llm=llm,
        db=LangchainSQLDatabase(
            engine=engine,
            schema=(None if db_schema == '' else db_schema),
            indexes_in_table_info=True,
        ),
        top_k=100,
        # return_intermediate_steps=True,
        use_query_checker=True,
        return_sql=True,
        verbose=LANGCHAIN_VERBOSE,
    )
    with get_openai_callback() as cb:
        result = db_chain(question_with_context)

    print(f"generate_query_with_langchain_sql_chain, result={result}, cb={cb}")

    intermediate_steps = format_intermediate_representations(
        result.get("intermediate_steps", [])
    )
    # sql_query = format_sql_query(result["intermediate_steps"][1])

    sql_query = extract_sql_query(result["result"])
    exec_time = time.time() - start_time

    print(
        f"sql_query={sql_query}, cost: {str(cb.total_cost)} tokens: {str(cb.total_tokens)} time: {str(exec_time)}"
    )
    response = {
        "response": result["result"],
        "intermediate_steps": intermediate_steps,
        "exec_time": exec_time,
        "total_tokens": cb.total_tokens,
        "total_cost": cb.total_cost,
        "sql_query": sql_query,
    }
    return response
