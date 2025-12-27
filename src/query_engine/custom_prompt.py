from config.settings.base import AGENT_LLM_MODEL, TEMPERATURE
from src.api.openapi_helpers import START_CODE_TAG, END_CODE_TAG
from src.db.utils import get_dialect_name
import openai

from src.query_engine.utils import extract_sql_custom


def generate_query_with_custom_prompt(
        question: str,
        table_names: list,
        db_type: str = "postgres",
        formatted_history: str = "",
):
    # print(f"generate_query, table_names={table_names}")
    db_dialect = get_dialect_name(db_type)
    table_prompt = ""
    table_history = ""

    if formatted_history:
        table_history = f"-- Chat History: {formatted_history} - Combine the chat history and follow up question into a standalone question."

    for i in range(len(table_names)):
        table_name = table_names[i]["table_name"]
        selected_table_columns = table_names[i]["table_columns"]
        foreign_keys = table_names[i]["foreign_keys"]
        examples = table_names[i]["examples"]
        # print(f"generate_query, table_name={table_name}, selected_table_columns={selected_table_columns}")

        filtered_columns = [column for column in selected_table_columns if '_airbyte' not in column["name"]]

        tabular_str = f"""-- Table={table_name}, columns={filtered_columns}, foreign_keys={foreign_keys}, examples={examples}. """
        table_prompt += tabular_str

    prompt = f"""
    -- Language {db_dialect}
    -- Tables: {table_prompt}
    {table_history}
    You are a SQL code translator. You have been given the Table data above. Your role is to translate natural language to {db_dialect}. 
    You should not select columns that are not part of the tables provided to you.
    Your only output should be SQL code. prefix the requested SQL code with {START_CODE_TAG} exactly and suffix the code with {END_CODE_TAG} exactly. Do not include any other text. Only SQL code. Always lowercase the values for comparisons (eg: lower(str)).
    Translate {question} to a syntactically-correct {db_dialect} query.
    """
    # print(
    #     f"generate_query, table_name={table_name}, table_columns={table_columns}, prompt={prompt}")
    system_text = f"you are a text-to-SQL translator. You write {db_dialect} code based on plain-language prompts.You should not select columns that are not part of the tables provided to you. "
    chat_query = [{"role": "system", "content": system_text},
                  {"role": "user", "content": prompt}]
    print(f"generate_query, chat_query={chat_query}")

    response = openai.ChatCompletion.create(
        messages=chat_query,
        model=AGENT_LLM_MODEL,
        temperature=TEMPERATURE,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=" ;",
    )
    # read the chat completion config and generate the required params to be passed to Chat Completion

    generated_query = extract_sql_custom(str(response["choices"][0]["message"]["content"]))

    return generated_query
