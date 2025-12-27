import re
import time
import traceback

from sqlalchemy.engine import Engine
# from langchain.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from config.settings.base import OPEN_API_TOKEN, AGENT_LLM_MODEL, LANGCHAIN_MAX_EXECUTION_TIME, \
    LANGCHAIN_MAX_ITERATIONS, TEMPERATURE, LANGCHAIN_VERBOSE

# from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain_community.agent_toolkits import SQLDatabaseToolkit


from llama_index.core import SQLDatabase as LangchainSQLDatabase

# from langchain.agents import initialize_agent
from langchain.agents import create_agent

# from langchain.agents.agent_types import AgentType
from langchain.callbacks import get_openai_callback
from langchain.schema import AgentAction
from langchain.embeddings import OpenAIEmbeddings
from langchain.agents.mrkl.base import ZeroShotAgent
from langchain.agents.agent import AgentExecutor
from langchain.chains.llm import LLMChain

from src.context_store.context_store import retrieve_context_for_question
from src.query_engine.langchain.agents.agent_toolkits.sql.experimental.toolkit import \
    SQLDatabaseToolkit as SQLDatabaseToolkitExperimental
from src.query_engine.langchain.agents.agent_toolkits.experimental.sql_database import \
    SQLDatabase as LangchainSQLDatabaseExperimental
from src.query_engine.langchain_sql_agent_prompts import PLAN_WITH_FEWSHOT_EXAMPLES_AND_INSTRUCTIONS, \
    SUFFIX_WITH_FEW_SHOT_SAMPLES, PLAN_WITH_FEWSHOT_EXAMPLES, PLAN_WITH_INSTRUCTIONS, SUFFIX_WITHOUT_FEW_SHOT_SAMPLES, \
    PLAN_BASE, AGENT_PREFIX, FORMAT_INSTRUCTIONS
from src.query_engine.utils import extract_sql_query

from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
from langchain.callbacks.streaming_stdout_final_only import FinalStreamingStdOutCallbackHandler
from langchain.schema import LLMResult
from uuid import UUID


# from src.query_engine.langchain.sql_database import SQLDatabase as LangchainSQLDatabase
# from src.query_engine.langchain.agents import initialize_agent

def format_intermediate_representations(
        intermediate_representation: List[Tuple[AgentAction, str]]
) -> List:
    """Formats the intermediate representation into a string."""
    formatted_intermediate_representation = []
    for item in intermediate_representation:
        formatted_intermediate_representation.append(
            {
                "thought": f"{str(item[0].log).split('Action:')[0]}",
                "action": f"{item[0].tool}",
                "action_input": f"{item[0].tool_input}",
                "observation": f"{item[1]}"
            }
        )
    return formatted_intermediate_representation


class CustomStreamingStdOutCallbackHandler(FinalStreamingStdOutCallbackHandler):
    buffer: List[Tuple[str, float]] = []
    stop_token = "#!stop!#"

    def on_llm_start(
            self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        super().on_llm_start(serialized, prompts, **kwargs)
        self.buffer = []

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        self.add_to_buffer(self.stop_token)

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        # Remember the last n tokens, where n = len(answer_prefix_tokens)
        self.last_tokens.append(token)
        if len(self.last_tokens) > len(self.answer_prefix_tokens):
            self.last_tokens.pop(0)

        # Check if the last n tokens match the answer_prefix_tokens list ...
        if self.last_tokens == self.answer_prefix_tokens:
            self.answer_reached = True
            # Do not print the last token in answer_prefix_tokens,
            # as it's not part of the answer yet
            return

        # ... if yes, then append tokens to buffer
        if self.answer_reached:
            self.add_to_buffer(token)

    def add_to_buffer(self, token: str) -> None:
        now = datetime.now()
        self.buffer.append((token, now))

    def stream_chars(self):
        while True:
            # when we didn't receive any token yet, just continue
            if len(self.buffer) == 0:
                continue

            token, timestamp = self.buffer.pop(0)

            if token != self.stop_token:
                for character in token:
                    yield (character, timestamp)
                    time.sleep(0.2)  # Remove this line. It's just for illustration purposes
            else:
                break


def generate_query_with_langchain_custom_agent(
        question: str,
        engine: Engine = None,
        context: List[dict] = None,
        db_schema=None,
        company_id=None,
        resourcename=None,
        genie_users_id=None,
        is_experimental=False,
        list_tables=None,
        db_warehouse=None,
        ai_model=AGENT_LLM_MODEL,
        ai_temp=TEMPERATURE,
):
    number_of_instructions = len(context)
    max_examples = 20

    start_time = time.time()

    llm = ChatOpenAI(model_name=ai_model, openai_api_key=OPEN_API_TOKEN, temperature=ai_temp)

    if is_experimental:
        db = LangchainSQLDatabaseExperimental(
            engine=engine,
            schema=(None if db_schema == '' else db_schema),
            indexes_in_table_info=True,
        )
    else:
        db = LangchainSQLDatabase(
            engine=engine,
            schema=(None if db_schema == '' else db_schema),
            indexes_in_table_info=True,
        )

    if is_experimental:
        samples, security_instructions = retrieve_context_for_question(
            question=question,
            company_id=company_id,
            genie_users_id=genie_users_id,
            resourcename=resourcename,
            db_schema=db_schema,
            number_of_samples=10,
            db_warehouse=db_warehouse,
        )
        print(
            f"generate_query_with_langchain_custom_agent, list_tables={len(list_tables)} samples={len(samples)}, security_instructions={len(security_instructions)}")
        toolkit = SQLDatabaseToolkitExperimental(
            db=db,
            context=context,
            few_shot_examples=samples,
            security_instructions=security_instructions,
            db_scan=list_tables,
            embedding=OpenAIEmbeddings(
                openai_api_key=OPEN_API_TOKEN,
                model="text-embedding-ada-002",
            ),
        )
        tools = toolkit.get_tools()
        if max_examples > 0 and number_of_instructions > 0:
            plan = PLAN_WITH_FEWSHOT_EXAMPLES_AND_INSTRUCTIONS
            suffix = SUFFIX_WITH_FEW_SHOT_SAMPLES
        elif max_examples > 0:
            plan = PLAN_WITH_FEWSHOT_EXAMPLES
            suffix = SUFFIX_WITH_FEW_SHOT_SAMPLES
        elif number_of_instructions > 0:
            plan = PLAN_WITH_INSTRUCTIONS
            suffix = SUFFIX_WITHOUT_FEW_SHOT_SAMPLES
        else:
            plan = PLAN_BASE
            suffix = SUFFIX_WITHOUT_FEW_SHOT_SAMPLES
        plan = plan.format(
            dialect=toolkit.dialect,
            max_examples=max_examples,
        )
        prefix = AGENT_PREFIX.format(
            dialect=toolkit.dialect, max_examples=max_examples, agent_plan=plan
        )
        prompt = ZeroShotAgent.create_prompt(
            tools,
            prefix=prefix,
            suffix=suffix,
            format_instructions=FORMAT_INSTRUCTIONS,
            # input_variables=input_variables,
        )
        llm_chain = LLMChain(
            llm=llm,
            prompt=prompt,
        )
        tool_names = [tool.name for tool in tools]
        agent = ZeroShotAgent(llm_chain=llm_chain, allowed_tools=tool_names)
        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=tools,
            handle_parsing_errors=True,
            return_intermediate_steps=True,
            max_execution_time=LANGCHAIN_MAX_EXECUTION_TIME,
            max_iterations=LANGCHAIN_MAX_ITERATIONS,
            use_query_checker=True,
            verbose=LANGCHAIN_VERBOSE,
            # return_sql=True,
        )
    else:
        tools = SQLDatabaseToolkit(
            db=db,
            llm=llm
        ).get_tools()
        agent_executor = create_agent(
            tools,
            llm,
            system_prompt="A zero shot agent that does a reasoning step before acting.",
            # agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            # handle_parsing_errors=True,
            # return_intermediate_steps=True,
            # max_execution_time=LANGCHAIN_MAX_EXECUTION_TIME,
            # max_iterations=LANGCHAIN_MAX_ITERATIONS,
            # use_query_checker=True,
            # return_sql=True,
        )
    if context is not None:
        samples_prompt_string = "The following are some similar previous questions and their correct SQL queries from these databases: \
                \n"
        for sample in context:
            samples_prompt_string += (
                f"Question: {sample['question']} \nSQL: {sample['answer']} \n"
            )

    question_with_context = (
        f"{question} An example of a similar question and the query that was generated \
                                    to answer it is the following {samples_prompt_string}"
        if context is not None
        else question
    )
    with get_openai_callback() as cb:
        result = agent_executor(question_with_context)
    sql_query_list = []
    for step in result.get("intermediate_steps", []):
        action = step[0]
        if type(action) is AgentAction and action.tool == "sql_db_query":
            print(f"generate_query_with_langchain_custom_agent, action.tool_input={action.tool_input}")
            sql_query = extract_sql_query(action.tool_input)
            print(f"generate_query_with_langchain_custom_agent, sql_query={sql_query}")
            sql_query_list.append(
                sql_query
            )
    intermediate_steps = format_intermediate_representations(
        result.get("intermediate_steps", [])
    )
    exec_time = time.time() - start_time
    print(
        f"cost: {str(cb.total_cost)} tokens: {str(cb.total_tokens)} time: {str(exec_time)}, result={result}"
    )
    ai_response = result["output"]
    sql_query = sql_query_list[-1] if len(sql_query_list) > 0 else ""
    if not sql_query:
        print(
            F"generate_query_with_langchain_custom_agent, ERROR: FAILED TO GET VALID SQL. check if we can get it from the AI response")
        attempt_sql = extract_sql_query_from_ai_response(ai_response)
        if attempt_sql:
            print(
                F"generate_query_with_langchain_custom_agent, ERROR: FALLBACK GOT VALID SQL FROM ai_response! attempt_sql={attempt_sql}")
            sql_query = attempt_sql

    # if sql_query:
    #     sql_query = format_sql_query(sql_query)

    response = {
        "response": ai_response,
        "intermediate_steps": intermediate_steps,
        "exec_time": exec_time,
        "total_tokens": cb.total_tokens,
        "total_cost": cb.total_cost,
        "sql_query": sql_query,
    }
    print(f"generate_query_with_langchain_custom_agent, response={response}")
    return response


def extract_sql_query_from_ai_response(ai_response):
    try:
        # Pattern to match an SQL query
        patterns = [
            r'(```sql\s*)(SELECT.*?;)(\s*```)',  # For queries within ```sql ... ```
            r'(SELECT.*?;)'  # For direct queries not in a Markdown code block
        ]

        for pattern in patterns:
            match = re.search(pattern, ai_response, re.DOTALL | re.IGNORECASE)
            if match:
                # Return the SQL query part only, excluding possible Markdown code block syntax
                return match.group(1).strip()

    except Exception as e:
        traceback.print_exc()
        print(f"extract_sql_query, Catch Exception, ai_response={ai_response}: error={e}")
