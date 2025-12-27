from psycopg2 import sql, Error


def create_approved_questions(conn, question, answer, company_id, approved_by, chart_code, db_schema, resourcename, db_warehouse):
    cur = conn.cursor()
    try:
        # Create user
        insert = sql.SQL(
            """
            INSERT INTO genie_approved_questions (question, answer, datetime, company_id, approved_by, chart_code, db_schema, resourcename, db_warehouse) 
            VALUES (%s, %s, NOW(), %s, %s, %s, %s, %s, %s) 
            RETURNING id
            """
        )
        print(
            f"create_approved_questions, question={question}, answer={answer}, company_id={company_id}, approved_by={approved_by}, chart_code={chart_code}, db_schema={db_schema}, resourcename={resourcename}, db_warehouse={db_warehouse}")
        values = (question, answer, company_id, approved_by, chart_code, db_schema, resourcename, db_warehouse)

        cur.execute(insert, values)
        generated_id = cur.fetchone()[0]

        return generated_id
    except Error as e:
        print(f"create_approved_questions, Database error: {e}")
        return False

    finally:
        conn.commit()
        cur.close()
        conn.close()


def get_approved_questions_by_id(conn, company_id, id):
    cur = conn.cursor()

    try:
        query = """
            SELECT id, question, answer, datetime, company_id, approved_by, chart_code, db_schema, resourcename, db_warehouse
            FROM genie_approved_questions 
            WHERE company_id = %s
            AND id = %s            
        """
        cur.execute(query, (company_id, id))
        results = cur.fetchall()

        history = []
        for result in results:
            history_entry = {
                "id": result[0],
                "question": result[1],
                "answer": result[2],
                "datetime": result[3],
                "company_id": result[4],
                "approved_by": result[5],
                "chart_code": result[6],
                "db_schema": result[7],
                "resourcename": result[8],
                "db_warehouse": result[9],
            }
            history.append(history_entry)

        return history
    except Exception as e:
        print(f"get_approved_question_by_id, Database error: {e}")
        return None
    finally:
        cur.close()
        conn.close()


def get_approved_questions_by_company_id(conn, company_id, limit=10, skip=0):
    cur = conn.cursor()

    try:
        query = """
            SELECT id, question, answer, datetime, company_id, approved_by, chart_code, db_schema, resourcename, db_warehouse
            FROM genie_approved_questions 
            WHERE company_id = %s 
            LIMIT %s OFFSET %s                   
        """
        cur.execute(query, (company_id, limit, skip))
        results = cur.fetchall()

        history = []
        for result in results:
            history_entry = {
                "id": result[0],
                "question": result[1],
                "answer": result[2],
                "datetime": result[3],
                "company_id": result[4],
                "approved_by": result[5],
                "chart_code": result[6],
                "db_schema": result[7],
                "resourcename": result[8],
                "db_warehouse": result[9],
            }
            history.append(history_entry)

        return history
    except Exception as e:
        print(f"get_approved_question_by_company_id, Database error: {e}")
        return None
    finally:
        cur.close()
        conn.close()


def delete_approved_questions_by_id(conn, id):
    cur = conn.cursor()

    delete = sql.SQL(
        """
        DELETE FROM genie_approved_questions
        WHERE id = %s
        """
    )

    values = (id,)

    try:
        cur.execute(delete, values)
        rows_deleted = cur.rowcount
        if rows_deleted == 0:
            print(f"No rows deleted, ID {id} might not exist.")
            return False
        else:
            print(f"Successfully deleted approved_questions with ID {id}")
            return True
    except Error as e:
        print(f"delete_approved_questions_by_id, Database error: {e}")
        return False
    finally:
        conn.commit()  # Commit the transaction
        cur.close()
        conn.close()
