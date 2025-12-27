import datetime
import traceback
import pytz
from psycopg2 import sql, Error


def get_database_connection_by_company_id(conn, company_id: int):
    cur = conn.cursor()

    try:
        select = sql.SQL(
            """
            SELECT name, host, port, ssl, databasename, username, password, apikey, resourcename, datetime, connection_string_url, db_type, company_id 
            FROM genie_users_database_connection 
            WHERE company_id = %s
            """
        )
        print(f"get_database_connection_by_company_id, company_id={company_id}")
        values = (company_id,)

        cur.execute(select, values)
        results = cur.fetchall()

        # Format results
        connections = []
        for result in results:
            connection = {
                "name": result[0],
                "host": result[1],
                "port": result[2],
                "ssl": result[3],
                "databasename": result[4],
                "username": result[5],
                "password": result[6],
                "apikey": result[7],
                "resourcename": result[8],
                "datetime": result[9],
                "connection_string_url": result[10],
                "db_type": result[11],
                "company_id": result[12],
            }
            connections.append(connection)
        return connections

    except Exception as e:
        print(f"list_genie_users_db_guardrails, Database error: {e}")
        traceback.print_exc()
        return []

    finally:
        cur.close()
        conn.close()


def get_user_db(conn, user_id: int):
    cur = conn.cursor()

    select = sql.SQL(
        """
        SELECT name, host, port, ssl, databasename, username, password, apikey, resourcename, datetime, connection_string_url, db_type, company_id 
        FROM genie_users_database_connection 
        WHERE genie_users_id = %s
        """
    )
    print(f"get_user_db, user_id={user_id}")
    values = (user_id,)

    cur.execute(select, values)
    results = cur.fetchall()

    # Close the connection
    cur.close()
    conn.close()

    # Format results
    if results:
        connections = []
        for result in results:
            connection = {
                "name": result[0],
                "host": result[1],
                "port": result[2],
                "ssl": result[3],
                "databasename": result[4],
                "username": result[5],
                "password": result[6],
                "apikey": result[7],
                "resourcename": result[8],
                "datetime": result[9],
                "connection_string_url": result[10],
                "db_type": result[11],
                "company_id": result[12],
            }
            connections.append(connection)
        return connections
    else:
        return []


def create_or_update_user_db_connection(
        conn, user_id, name, host, port, ssl,
        databasename, username, password, apikey,
        resourcename, connection_string_url, db_type,
        company_id
):
    cur = conn.cursor()
    try:
        # First, check if a record exists with the provided parameters
        select = sql.SQL(
            "SELECT id FROM genie_users_database_connection WHERE genie_users_id = %s AND resourcename = %s"
        )
        select_values = (user_id, resourcename)
        cur.execute(select, select_values)

        # Fetch result of the select statement
        result = cur.fetchone()
        now = datetime.datetime.now(tz=pytz.UTC)

        if result:
            # If a record exists, perform an update
            print(
                f"create_or_update_user_db_connection, a record exists, perform an update, user_id={user_id}, company_id={company_id}, db_type={db_type}")
            update = sql.SQL(
                """
                    UPDATE genie_users_database_connection 
                        SET name = %s, host = %s, port = %s, ssl = %s, username = %s, password = %s, apikey = %s, resourcename = %s, genie_users_id = %s, 
                        databasename = %s, datetime = %s, connection_string_url = %s, db_type = %s 
                    WHERE genie_users_id = %s AND resourcename = %s
                """
            )
            values = (
                name, host, port, ssl, username, password, apikey, resourcename, user_id,
                databasename, now, connection_string_url, db_type,
                user_id, resourcename
            )

            cur.execute(update, values)

            return result[0]
        else:
            # If no record exists, perform an insert
            print(
                f"create_or_update_user_db_connection, no record exists, perform an insert, user_id={user_id}, company_id={company_id}, db_type={db_type}")
            insert = sql.SQL(
                """
                    INSERT INTO genie_users_database_connection 
                        (name, host, port, ssl, databasename, username, password, apikey, resourcename, 
                            genie_users_id, datetime, connection_string_url, db_type, company_id) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 
                            %s, %s, %s, %s, %s)  RETURNING id
                """
            )
            values = (
                name, host, port, ssl, databasename, username, password, apikey, resourcename,
                user_id, now, connection_string_url, db_type, company_id
            )

            cur.execute(insert, values)
            generated_id = cur.fetchone()[0]

            return generated_id
    except Error as e:
        print(f"create_or_update_user_db_connection, Database error: {e}")
        traceback.print_exc()
        return None
    finally:
        conn.commit()
        cur.close()
        conn.close()
