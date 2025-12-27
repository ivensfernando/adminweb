from psycopg2 import sql
import traceback

from src.db.login_helpers import getConn
from src.db.table_info_helpers import get_genie_users_db_connection_details_by_company_id


def create_or_update_genie_users_db_guardrails(conn, table_name, db_schema, resourcename, company_id, genie_users_id,
                                               table_column, access_type, db_warehouse):
    cur = conn.cursor()

    if not db_schema:
        db_schema = ""
    if not db_warehouse:
        db_warehouse = ""

    try:
        # First, check if a record exists with the provided parameters
        select = sql.SQL(
            """
            SELECT id FROM genie_users_db_guardrails 
            WHERE table_name = %s AND 
            db_schema = %s AND 
            db_warehouse = %s AND 
            resourcename = %s AND 
            company_id = %s AND 
            genie_users_id = %s AND 
            table_column = %s
            """
        )
        select_values = (
            table_name, db_schema, db_warehouse, resourcename, company_id, genie_users_id,
            table_column)
        cur.execute(select, select_values)

        # Fetch result of the select statement
        result = cur.fetchone()

        if result:
            # If a record exists, perform an update
            update = sql.SQL(
                """
                UPDATE genie_users_db_guardrails SET access_type = %s 
                WHERE 
                table_name = %s AND 
                db_schema = %s AND 
                db_warehouse = %s AND 
                resourcename = %s AND 
                company_id = %s AND 
                genie_users_id = %s AND 
                table_column = %s
                """
            )
            update_values = (
                access_type,
                table_name, db_schema, db_warehouse, resourcename, company_id,
                genie_users_id, table_column)
            cur.execute(update, update_values)
            return result[0]  # Return existing ID
        else:
            # If no record exists, perform an insert
            insert = sql.SQL(
                """INSERT INTO genie_users_db_guardrails 
                (table_name, db_schema, resourcename, company_id, genie_users_id, table_column, access_type, db_warehouse) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id"""
            )
            insert_values = (
                table_name, db_schema, resourcename, company_id, genie_users_id, table_column, access_type,
                db_warehouse)
            cur.execute(insert, insert_values)
            generated_id = cur.fetchone()[0]
            return generated_id  # Return new ID

    except Exception as e:
        print(f"create_or_update_genie_users_db_guardrails, Database error: {e}")
        traceback.print_exc()
        return None

    finally:
        conn.commit()
        cur.close()
        conn.close()


def list_genie_users_db_guardrails(conn, db_schema, db_warehouse, resourcename, company_id, genie_users_id):
    cur = conn.cursor()

    if not db_schema:
        db_schema = ""
    if not db_warehouse:
        db_warehouse = ""

    try:
        # Query to select genie_users_db_guardrails records based on specified criteria
        select = sql.SQL(
            """
            SELECT id, table_name, db_schema, resourcename, company_id, genie_users_id, table_column, access_type, datetime, db_warehouse
            FROM genie_users_db_guardrails 
            WHERE 
            db_schema = %s AND 
            db_warehouse = %s AND 
            resourcename = %s AND 
            company_id = %s AND 
            genie_users_id = %s
            """
        )
        values = (db_schema, db_warehouse, resourcename, company_id, genie_users_id)

        cur.execute(select, values)
        records = cur.fetchall()

        # Format the records into a list of dictionaries
        guardrails_data = []
        for record in records:
            guardrail_entry = {
                "id": record[0],
                "table_name": record[1],
                "db_schema": record[2],
                "resourcename": record[3],
                "company_id": record[4],
                "genie_users_id": record[5],
                "table_column": record[6],
                "access_type": record[7],
                "datetime": record[8],
                "db_warehouse": record[9],
            }
            guardrails_data.append(guardrail_entry)

        return guardrails_data

    except Exception as e:
        print(f"list_genie_users_db_guardrails, Database error: {e}")
        traceback.print_exc()
        return []

    finally:
        cur.close()
        conn.close()


def list_genie_users_db_guardrails(conn, db_schema, db_warehouse, resourcename, company_id, genie_users_id):
    cur = conn.cursor()

    if not db_schema:
        db_schema = ""
    if not db_warehouse:
        db_warehouse = ""

    try:
        # Query to select genie_users_db_guardrails records based on specified criteria
        select = sql.SQL(
            """
            SELECT id, table_name, db_schema, resourcename, company_id, genie_users_id, table_column, access_type, datetime, db_warehouse
            FROM genie_users_db_guardrails 
            WHERE 
            db_schema = %s AND 
            db_warehouse = %s AND 
            resourcename = %s AND 
            company_id = %s AND 
            genie_users_id = %s
            """
        )
        values = (db_schema, db_warehouse, resourcename, company_id, genie_users_id)

        cur.execute(select, values)
        records = cur.fetchall()

        # Format the records into a list of dictionaries
        guardrails_data = []
        for record in records:
            guardrail_entry = {
                "id": record[0],
                "table_name": record[1],
                "db_schema": record[2],
                "resourcename": record[3],
                "company_id": record[4],
                "genie_users_id": record[5],
                "table_column": record[6],
                "access_type": record[7],
                "datetime": record[8],
                "db_warehouse": record[9],
            }
            guardrails_data.append(guardrail_entry)

        return guardrails_data

    except Exception as e:
        print(f"list_genie_users_db_guardrails, Database error: {e}")
        traceback.print_exc()
        return []

    finally:
        cur.close()
        conn.close()


def get_merged_db_details_and_guardrails(db_schema, resourcename, company_id, genie_users_id, skip=0, limit=100, db_warehouse=None):
    # Fetch details from both functions
    guardrails = list_genie_users_db_guardrails(
        conn=getConn(),
        db_schema=db_schema,
        resourcename=resourcename,
        company_id=company_id,
        genie_users_id=genie_users_id,
        db_warehouse=db_warehouse,
    )
    print(f"get_merged_db_details_and_guardrails, guardrails, guardrails_len={len(guardrails)}")

    db_details = get_genie_users_db_connection_details_by_company_id(
        conn=getConn(),
        company_id=company_id,
        db_schema=db_schema,
        resourcename=resourcename,
        db_warehouse=db_warehouse,
        skip=skip,
        limit=limit,
    )
    print(f"get_merged_db_details_and_guardrails, db_details, db_details_len={len(db_details)}")

    # Convert guardrails to a more searchable format
    guardrails_dict = {}
    for gr in guardrails:
        key = (gr['table_name'], gr['db_schema'] if gr['db_schema'] else "", gr['resourcename'], gr['table_column'])
        guardrails_dict[key] = gr['access_type']

    # Iterate over db_details and merge with guardrails
    for detail in db_details:
        schema = detail['db_schema'] if detail['db_schema'] else ""
        for column in detail['table_columns']:
            column_key = (detail['table_name'], schema, detail['resourcename'], column['name'])
            column['access_type'] = guardrails_dict.get(column_key, 0)  # Default to 0 if not found

    return db_details
