import logging
import traceback
from typing import List, Tuple

from sql_metadata import Parser

from src.context_store.pinecone_store import pinecone_add_record, pinecone_query, pinecone_delete_record
from src.db.guardrails import list_genie_users_db_guardrails
from src.db.history import get_history_by_id
from src.db.login_helpers import getConn

logger = logging.getLogger(__name__)

GOLDEN_RECORDS_INDEX_NAME = "golden-records"


def retrieve_context_for_question(
        question: str,
        company_id: str,
        genie_users_id: str,
        resourcename: str,
        db_schema: str,
        number_of_samples: int = 3,
        db_warehouse: str = "",
) -> Tuple[List[dict] | None, List[dict] | None]:
    logger.info(f"Getting context for {question}")
    try:
        # TODO: add db_warehouse ?
        closest_questions = pinecone_query(
            query_text=question,
            company_id=company_id,
            index_name=GOLDEN_RECORDS_INDEX_NAME,
            num_results=number_of_samples,
            resourcename=resourcename,
            db_schema=db_schema,
        )
    except Exception as e:
        print(f"Error, retrieve_context_for_question, pinecone_query: error={e}")
        traceback.print_exc()
        closest_questions = []

    samples = []

    for question in closest_questions:
        id = question["id"]
        golden_record = get_history_by_id(
            conn=getConn(),
            company_id=company_id,
            id=id
        )
        if golden_record is not None:
            samples.append(
                {
                    "question": golden_record["question"],
                    "answer": golden_record["answer"],
                    "score": question["score"],
                }
            )

    instructions = list_genie_users_db_guardrails(
        conn=getConn(),
        db_schema=db_schema,
        db_warehouse=db_warehouse,
        resourcename=resourcename,
        company_id=company_id,
        genie_users_id=genie_users_id,
    )

    return samples, instructions


def add_golden_records(
        golden_records: List,
        company_id: str,
        resourcename: str,
        db_schema: str,
) -> List:
    returned_golden_records = []
    for record in golden_records:
        question = record["question"]
        answer = record["answer"]
        id = record["id"]
        tables = Parser(answer).tables
        tables_used = tables[0]
        golden_record = {
            "question": question,
            "answer": answer,
        }
        returned_golden_records.append(golden_record)
        pinecone_add_record(
            documents=question,
            company_id=company_id,
            index_name=GOLDEN_RECORDS_INDEX_NAME,
            metadata=[
                {
                    "tables_used": tables_used,
                    "resourcename": resourcename,
                    "db_schema": db_schema,
                }
            ],  # this should be updated for multiple tables
            ids=[str(id)],
        )
    return returned_golden_records


def remove_golden_records(company_id: str, ids: List) -> bool:
    for id in ids:
        pinecone_delete_record(
            index_name=GOLDEN_RECORDS_INDEX_NAME,
            company_id=company_id,
            id=id
        )
    return True
