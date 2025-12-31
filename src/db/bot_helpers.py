import traceback

from psycopg2 import sql, Error


def get_bot_users_by_email(conn, email):
    if conn is None:
        return []
    cur = conn.cursor()
    try:
        select = sql.SQL(
            """
            SELECT u.id, u.email
            FROM users u
            WHERE u.email = %s
            """
        )
        cur.execute(select, (email,))
        rows = cur.fetchall()
        return [{"id": row[0], "email": row[1]} for row in rows] if rows else []
    except Error as e:
        print(f"get_bot_users_by_email, Database error: {e}")
        traceback.print_exc()
        return []
    finally:
        cur.close()
        conn.close()


def get_user_exchanges_by_user_ids(conn, user_ids):
    if conn is None:
        return []
    if not user_ids:
        conn.close()
        return []
    cur = conn.cursor()
    try:
        select = sql.SQL(
            """
            SELECT ue.id,
                   ue.user_id,
                   ue.exchange_id,
                   ue.run_on_server,
                   ex.name AS exchange_name
            FROM user_exchanges ue
            LEFT JOIN exchanges ex ON ex.id = ue.exchange_id
            WHERE ue.user_id = ANY(%s)
            """
        )
        cur.execute(select, (user_ids,))
        rows = cur.fetchall()
        return [
            {
                "id": row[0],
                "user_id": row[1],
                "exchange_id": row[2],
                "run_on_server": row[3],
                "exchange_name": row[4],
            }
            for row in rows
        ] if rows else []
    except Error as e:
        print(f"get_user_exchanges_by_user_ids, Database error: {e}")
        traceback.print_exc()
        return []
    finally:
        cur.close()
        conn.close()
