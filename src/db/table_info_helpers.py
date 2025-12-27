import json
import traceback
from datetime import datetime

from psycopg2 import sql


def create_genie_users_db_connection_details(
        conn, table_name, table_columns, foreign_keys, examples, company_id,
        genie_users_id, status="COMPLETED", db_schema="",
        resourcename="", description="", table_schema="", db_warehouse=""
):
    cur = conn.cursor()
    if db_schema is None:
        db_schema = ""
    if db_warehouse is None:
        db_warehouse = ""
    try:
        # Create record
        insert = sql.SQL(
            """
                INSERT INTO genie_users_db_connection_details 
                    (table_name, table_columns, foreign_keys, examples, datetime, company_id, genie_users_id, status, db_schema, resourcename, description, table_schema, db_warehouse) 
                VALUES 
                    (%s, %s, %s, %s, NOW(), %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (company_id, table_name, db_schema, db_warehouse, resourcename)
                DO UPDATE SET
                    table_columns = EXCLUDED.table_columns,
                    foreign_keys = EXCLUDED.foreign_keys,
                    examples = EXCLUDED.examples,
                    datetime = NOW(),
                    genie_users_id = EXCLUDED.genie_users_id,
                    status = EXCLUDED.status,
                    description = EXCLUDED.description,
                    table_schema = EXCLUDED.table_schema
                RETURNING id;
            """
        )

        print(
            f"create_genie_users_db_connection_details, table_name={table_name}, table_columns={table_columns}, foreign_keys={foreign_keys}, examples={examples}, company_id={company_id}, genie_users_id={genie_users_id}, status={status} ")
        values = (table_name, json.dumps(table_columns), json.dumps(foreign_keys), json.dumps(examples), company_id,
                  genie_users_id, status, db_schema, resourcename, description, table_schema, db_warehouse)

        cur.execute(insert.as_string(conn), values)
        generated_id = cur.fetchone()[0]

        return generated_id

    except Exception as e:
        traceback.print_exc()
        print(f"create_genie_users_db_connection_details, Database error: {e}")
        return False

    finally:
        conn.commit()
        cur.close()
        conn.close()


def get_genie_users_db_connection_details_by_company_id(
        conn, company_id, db_schema="", resourcename="", skip=0,
        limit=100, db_warehouse="",
):
    cur = conn.cursor()

    if db_schema is None:
        db_schema = ""
    if db_warehouse is None:
        db_warehouse = ""

    print(
        f"get_genie_users_db_connection_details_by_company_id, company_id={company_id}, resourcename={resourcename}, db_schema={db_schema}, skip={skip}, limit={limit}")
    # Base query to select genie_users_db_connection_details based on company_id
    select = sql.SQL(
        """
        SELECT 
                d.id, 
                d.table_name, 
                d.table_columns, 
                d.foreign_keys, 
                d.examples, 
                d.datetime, 
                d.status, 
                d.genie_users_id,
                d.company_id,
                d.db_schema,
                d.resourcename,
                d.description,
                d.table_schema,
                d.db_warehouse
            FROM genie_users_db_connection_details d
            WHERE 
                d.company_id = %s 
                AND d.resourcename = %s  
                AND d.db_schema = %s  
                AND d.db_warehouse = %s 
            LIMIT %s OFFSET %s
        """
    )

    # If skip and limit are provided, append them to the base query
    values = (int(company_id), resourcename, db_schema, db_warehouse, limit, skip)

    try:
        cur.execute(select, values)
        details_records = cur.fetchall()

        details_data = []
        for record in details_records:
            detail_entry = {
                "id": record[0],
                "table_name": record[1],
                "table_columns": record[2],
                "foreign_keys": record[3],
                "examples": record[4],
                "datetime": record[5],
                "status": record[6],
                "genie_users_id": record[7],
                "company_id": record[8],
                "db_schema": None if record[9] == '' else record[9],
                "resourcename": record[10],
                "description": record[11],
                "table_schema": record[12],
                "db_warehouse": None if record[13] == '' else record[13],
            }
            details_data.append(detail_entry)

        return details_data
    except Exception as e:
        traceback.print_exc()
        print(f"get_genie_users_db_connection_details_by_company_id, Database error: {e}")
        return []
    finally:
        cur.close()
        conn.close()


def get_genie_users_db_connection_details_by_company_id_join_column_description(
        conn, company_id, db_schema="", resourcename="", skip=0,
        limit=100, db_warehouse="",
):
    cur = conn.cursor()

    if db_schema is None:
        db_schema = ""
    if db_warehouse is None:
        db_warehouse = ""

    print(
        f"get_genie_users_db_connection_details_by_company_id_join_column_description, company_id={company_id}, resourcename={resourcename}, db_schema={db_schema}, skip={skip}, limit={limit}")
    # Base query to select genie_users_db_connection_details based on company_id
    select = sql.SQL(
        """
        SELECT 
            d.id, 
            d.table_name, 
            d.table_columns, 
            d.foreign_keys, 
            d.examples, 
            d.datetime, 
            d.status, 
            d.genie_users_id,
            d.company_id,
            d.db_schema,
            d.resourcename,
            d.description,
            d.table_schema,
            d.db_warehouse,
            json_agg(
                json_build_object(
                    'id', cd.id,
                    'column_name', cd.column_name,
                    'column_description', cd.column_description,
                    'column_distinct', cd.column_distinct
                )
            ) FILTER (WHERE cd.id IS NOT NULL) AS column_description_list
        FROM genie_users_db_connection_details d
        LEFT JOIN genie_users_db_connection_details_column_description cd ON
            d.company_id = cd.company_id AND
            d.table_name = cd.table_name AND
            d.db_schema = cd.db_schema AND
            d.db_warehouse = cd.db_warehouse AND
            d.resourcename = cd.resourcename
        WHERE 
            d.company_id = %s 
            AND d.resourcename = %s  
            AND d.db_schema = %s  
            AND d.db_warehouse = %s 
        GROUP BY 
            d.id, 
            d.table_name, 
            d.table_columns, 
            d.foreign_keys, 
            d.examples, 
            d.datetime, 
            d.status, 
            d.genie_users_id,
            d.company_id,
            d.db_schema,
            d.resourcename,
            d.description,
            d.table_schema,
            d.db_warehouse
        LIMIT %s OFFSET %s;
        """
    )

    # If skip and limit are provided, append them to the base query
    values = (int(company_id), resourcename, db_schema, db_warehouse, limit, skip)

    try:
        cur.execute(select, values)
        details_records = cur.fetchall()

        details_data = []
        for record in details_records:
            detail_entry = {
                "id": record[0],
                "table_name": record[1],
                "table_columns": record[2],
                "foreign_keys": record[3],
                "examples": record[4],
                "datetime": record[5],
                "status": record[6],
                "genie_users_id": record[7],
                "company_id": record[8],
                "db_schema": None if record[9] == '' else record[9],
                "resourcename": record[10],
                "description": record[11],
                "table_schema": record[12],
                "db_warehouse": None if record[13] == '' else record[13],
                "column_description_list": record[14],
            }
            details_data.append(detail_entry)

        return details_data
    except Exception as e:
        traceback.print_exc()
        print(f"get_genie_users_db_connection_details_by_company_id_join_column_description, Database error: {e}")
        return []
    finally:
        cur.close()
        conn.close()


def create_genie_users_db_connection_details_column_description(
        conn, table_name, db_schema, db_warehouse, resourcename,
        company_id, column_name, column_description
):
    cur = conn.cursor()
    try:
        # UPSERT (Update or Insert) statement
        upsert = sql.SQL(
            """
            INSERT INTO genie_users_db_connection_details_column_description 
            (table_name, db_schema, db_warehouse, resourcename, company_id, column_name, column_description, datetime) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            ON CONFLICT (table_name, db_schema, db_warehouse, resourcename, company_id, column_name)
            DO UPDATE SET
            column_description = EXCLUDED.column_description
            RETURNING id
            """
        )

        print(
            f"create_genie_users_db_connection_details_column_description, table_name={table_name}, db_schema={db_schema}, db_warehouse={db_warehouse}, resourcename={resourcename}, company_id={company_id}, column_name={column_name}, column_description={column_description} ")
        values = (
            table_name, db_schema, db_warehouse, resourcename, company_id, column_name, column_description
        )

        cur.execute(upsert.as_string(conn), values)
        generated_id = cur.fetchone()[0]

        return generated_id

    except Exception as e:
        traceback.print_exc()
        print(f"create_genie_users_db_connection_details_column_description, Database error: {e}")
        return False

    finally:
        conn.commit()
        cur.close()
        conn.close()


def create_genie_users_db_connection_details_column_description_column_distinct(
        conn, table_name, db_schema, db_warehouse, resourcename,
        company_id, column_name, column_distinct
):
    cur = conn.cursor()
    try:
        # UPSERT (Update or Insert) statement
        upsert = sql.SQL(
            """
            INSERT INTO genie_users_db_connection_details_column_description 
            (table_name, db_schema, db_warehouse, resourcename, company_id, column_name, column_distinct, datetime) 
            VALUES (
            %s, %s, %s, %s, %s, %s, %s, NOW()
            )
            ON CONFLICT (table_name, db_schema, db_warehouse, resourcename, company_id, column_name)
            DO UPDATE SET
            column_distinct = EXCLUDED.column_distinct            
            RETURNING id
            """
        )

        print(
            f"create_genie_users_db_connection_details_column_description_column_distinct, table_name={table_name}, db_schema={db_schema}, db_warehouse={db_warehouse}, resourcename={resourcename}, company_id={company_id}, column_name={column_name}")
        values = (
            table_name, db_schema, db_warehouse, resourcename, company_id, column_name,
            json.dumps(column_distinct)
        )

        cur.execute(upsert.as_string(conn), values)
        generated_id = cur.fetchone()[0]

        return generated_id

    except Exception as e:
        traceback.print_exc()
        print(f"create_genie_users_db_connection_details_column_description_column_distinct, Database error: {e}")
        return False

    finally:
        conn.commit()
        cur.close()
        conn.close()


def get_genie_users_db_connection_details_column_description(
        conn, company_id, table_name, db_schema, db_warehouse,
        resourcename, column_name
):
    cur = conn.cursor()

    if not db_schema:
        db_schema = ""
    if not db_warehouse:
        db_warehouse = ""

    # Query data from genie_users_db_connection_details_column_description table
    select = sql.SQL(
        """
        SELECT id, table_name, db_schema, db_warehouse, resourcename, company_id, datetime, column_name, column_description 
        FROM genie_users_db_connection_details_column_description 
        WHERE 
            company_id = %s 
            AND table_name = %s 
            AND db_schema = %s  
            AND db_warehouse = %s  
            AND resourcename = %s 
            AND column_name = %s
        """
    )

    values = (company_id, table_name, db_schema, db_warehouse, resourcename, column_name)

    try:
        cur.execute(select, values)
        details = cur.fetchone()

        if details:
            return {
                "id": details[0],
                "table_name": details[1],
                "db_schema": details[2],
                "db_warehouse": details[3],
                "resourcename": details[4],
                "company_id": details[5],
                "datetime": details[6],
                "column_name": details[7],
                "column_description": details[8],
            }
        else:
            return None
    except Exception as e:
        print(f"get_genie_users_db_connection_details_column_description, Database error: {e}")
        return None
    finally:
        cur.close()
        conn.close()


def list_genie_users_db_connection_details_column_description(
        conn, company_id, table_name, db_schema, db_warehouse,
        resourcename
):
    cur = conn.cursor()

    if not db_schema:
        db_schema = ""
    if not db_warehouse:
        db_warehouse = ""

    # Query data from genie_users_db_connection_details_column_description table
    select = sql.SQL(
        """
        SELECT id, table_name, db_schema, db_warehouse, resourcename, company_id, datetime, column_name, column_description, column_distinct 
        FROM genie_users_db_connection_details_column_description 
        WHERE 
            company_id = %s AND 
            table_name = %s AND 
            db_schema = %s AND 
            db_warehouse = %s AND 
            resourcename = %s
        """
    )

    values = (company_id, table_name, db_schema, db_warehouse, resourcename)

    try:
        cur.execute(select, values)
        results = cur.fetchall()
        result_arr = []

        for result in results:
            entry = {
                "id": result[0],
                "table_name": result[1],
                "db_schema": result[2],
                "db_warehouse": result[3],
                "resourcename": result[4],
                "company_id": result[5],
                "datetime": result[6],
                "column_name": result[7],
                "column_description": result[8],
                "column_distinct": result[9],
            }
            result_arr.append(entry)

        return result_arr

    except Exception as e:
        print(f"list_genie_users_db_connection_details_column_description, Database error: {e}")
        return None
    finally:
        cur.close()
        conn.close()
