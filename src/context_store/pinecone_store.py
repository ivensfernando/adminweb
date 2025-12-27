from typing import Any, List
import pinecone
# from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings

from config.settings.base import OPEN_API_TOKEN, PINECONE_API_KEY, PINECONE_ENVIRONMENT, PINECONE_EMBEDDING_MODEL

pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)


def pinecone_query(
        query_text: str,
        company_id: str,
        # genie_users_id: str,
        index_name: str,
        num_results: int,
        resourcename: str,
        db_schema: str,
) -> list:
    indexes = pinecone.list_indexes()
    print(f"pinecone_query, indexes={indexes}")

    if index_name not in indexes:
        pinecone_create_index(index_name)

    index = pinecone.Index(index_name)

    embedding = OpenAIEmbeddings(
        openai_api_key=OPEN_API_TOKEN, model=PINECONE_EMBEDDING_MODEL
    )
    xq = embedding.embed_query(query_text)
    query_response = index.query(
        queries=[xq],
        filter={
            # "genie_users_id": {"$eq": genie_users_id},
            "resourcename": {"$eq": resourcename},
            "db_schema": {"$eq": db_schema},
        },
        top_k=num_results,
        include_metadata=True,
        namespace=str(company_id)
    )
    results = query_response.to_dict()["results"]
    if len(results):
        return results[0]["matches"]
    else:
        return []


def pinecone_add_record(
        company_id: str,
        documents: str,
        index_name: str,
        metadata: Any,
        ids: List,
):
    if index_name not in pinecone.list_indexes():
        pinecone_create_index(index_name)

    embedding = OpenAIEmbeddings(
        openai_api_key=OPEN_API_TOKEN, model=PINECONE_EMBEDDING_MODEL
    )
    index = pinecone.Index(index_name)
    embeds = embedding.embed_documents([documents])
    record = [(ids[0], embeds, metadata[0])]
    index.upsert(
        vectors=record,
        namespace=str(company_id)
    )


def pinecone_delete_record(index_name: str, company_id: str, id: str):
    if index_name not in pinecone.list_indexes():
        pinecone_create_index(index_name=index_name)

    index = pinecone.Index(index_name)
    index.delete(
        ids=[id],
        namespace=str(company_id)
    )


def pinecone_delete_index(index_name: str):
    return pinecone.delete_index(index_name)


def pinecone_create_index(index_name: str):
    pinecone.create_index(name=index_name, dimension=1536, metric="cosine")
