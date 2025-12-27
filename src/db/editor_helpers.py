from psycopg2 import sql, Error


def get_chat_history_by_id(conn, id):
    cur = conn.cursor()

    # Check user credentials
    select = sql.SQL(
        """
            SELECT  id, datetime, question, answer, genie_users_id, team_id_slack, user_id_slack,
            company_id, is_answered, db_schema, resourcename, ai_engine, results_len, db_warehouse
            FROM genie_chat_history 
            WHERE id = %s
        """
    )

    values = (id,)

    try:
        cur.execute(select, values)
        result = cur.fetchone()

        if result:
            return {
                "id": result[0],
                "datetime": result[1],
                "question": result[2],
                "answer": result[3],
                "genie_users_id": result[4],
                "team_id_slack": result[5],
                "user_id_slack": result[6],
                "company_id": result[7],
                "is_answered": result[8],
                "db_schema": result[9],
                "resourcename": result[10],
                "ai_engine": result[11],
                "results_len": result[12],
                "db_warehouse": result[13],
            }
        else:
            return None
    except Error as e:
        print(f"get_company_by_id, Database error: {e}")
        return None
    finally:
        cur.close()
        conn.close()


def update_chat_history_is_answered(conn, id, is_answered):
    cur = conn.cursor()
    try:
        # Update user password
        update = sql.SQL(
            "UPDATE genie_chat_history SET is_answered=%s WHERE id=%s"
        )

        print(f"update_chat_history_is_answered, is_answered={is_answered}, id={id}")
        values = (is_answered, id)

        cur.execute(update, values)

        # Check how many rows were affected to determine if the update was successful
        updated_rows = cur.rowcount
        if updated_rows == 1:
            return True
        else:
            print(f"update_chat_history_is_answered, No data found with id: {id}")
            return False

    except Error as e:
        print(f"update_chat_history_is_answered, Database error: {e}")
        return False

    finally:
        conn.commit()
        cur.close()
        conn.close()


def update_chat_history_answer_save(conn, id, answer):
    cur = conn.cursor()
    try:
        # Update user password
        update = sql.SQL(
            "UPDATE genie_chat_history SET answer=%s WHERE id=%s"
        )

        print(f"update_chat_history_answer_save, id={id}")
        values = (answer, id)

        cur.execute(update, values)

        # Check how many rows were affected to determine if the update was successful
        updated_rows = cur.rowcount
        if updated_rows == 1:
            return True
        else:
            print(f"update_chat_history_answer_save, No data found with id: {id}")
            return False

    except Error as e:
        print(f"update_chat_history_answer_save, Database error: {e}")
        return False

    finally:
        conn.commit()
        cur.close()
        conn.close()

def update_chat_history_chart_code_save(conn, id, chart_code):
    cur = conn.cursor()
    try:
        # Update user password
        update = sql.SQL(
            "UPDATE genie_chat_history SET chart_code=%s WHERE id=%s"
        )

        print(f"update_chat_history_chart_code_save, id={id}")
        values = (chart_code, id)

        cur.execute(update, values)

        # Check how many rows were affected to determine if the update was successful
        updated_rows = cur.rowcount
        if updated_rows == 1:
            return True
        else:
            print(f"update_chat_history_chart_code_save, No data found with id: {id}")
            return False

    except Error as e:
        print(f"update_chat_history_chart_code_save, Database error: {e}")
        return False

    finally:
        conn.commit()
        cur.close()
        conn.close()


def delete_chat_history(conn, id):
    cur = conn.cursor()
    try:
        # Update user password
        update = sql.SQL(
            "DELETE FROM genie_users WHERE id=%s"
        )

        print(f"delete_chat_history, id={id}")
        values = (id,)

        cur.execute(update, values)

        # Check how many rows were affected to determine if the update was successful
        updated_rows = cur.rowcount
        if updated_rows == 1:
            return True
        else:
            print(f"delete_chat_history, No genie_chat_history found with id: {id}")
            return False

    except Error as e:
        print(f"delete_chat_history, Database error: {e}")
        return False

    finally:
        conn.commit()
        cur.close()
        conn.close()
