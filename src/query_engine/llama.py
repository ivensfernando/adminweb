import traceback

from config.settings.base import OPEN_API_TOKEN, AGENT_LLM_MODEL
from llama_index import SQLDatabase
from langchain.chat_models import ChatOpenAI
from sqlalchemy import MetaData

from llama_index import (
    LLMPredictor,
    ServiceContext,
    VectorStoreIndex,
)
from llama_index.indices.struct_store import (
    SQLTableRetrieverQueryEngine,
)
from llama_index.objects import ObjectIndex, SQLTableNodeMapping, SQLTableSchema


def generate_sql_query_llama_index(engine, text_query):
    try:
        # Database Connection and Reflection
        metadata_obj = MetaData()
        metadata_obj.reflect(engine)

        # Initialize LLM Model
        llm = ChatOpenAI(model_name=AGENT_LLM_MODEL, openai_api_key=OPEN_API_TOKEN)

        llm_predictor = LLMPredictor(llm=llm)
        service_context = ServiceContext.from_defaults(
            llm_predictor=llm_predictor)  # You may need to add callbacks if necessary

        table_schema_objs = [SQLTableSchema(table_name=table_name) for table_name in metadata_obj.tables.keys()]

        table_node_mapping = SQLTableNodeMapping(SQLDatabase(engine=engine))

        # Object Indexing
        obj_index = ObjectIndex.from_objects(
            table_schema_objs,
            table_node_mapping,
            VectorStoreIndex
        )

        # Constructing the Query Engine
        query_engine = SQLTableRetrieverQueryEngine(
            SQLDatabase(engine=engine),
            obj_index.as_retriever(similarity_top_k=1),
            service_context=service_context
        )
        llama_result = query_engine.query(text_query)

        # Extracting SQL from the result
        generated_sql = llama_result.metadata["sql_query"]
        # score = 0
        # if evaluate == "simple":
        #     score = evaluate_sql_query_simple(text_query, generated_sql, SQLDatabase(engine=engine), llm, table_schema_objs)

    except Exception as e:
        print(f"generate_sql_query_llama_index, cant execute llama query_engine, e={e}")
        traceback.print_exc()
        return [], None

    return llama_result, generated_sql
