import calendar
import traceback

from psycopg2 import sql
import datetime
import pytz

from config.settings.base import AGENT_LLM_MODEL_CHART, TEMPERATURE


def get_history_by_question_hash(conn, question_hash, genie_users_id):
    cur = conn.cursor()

    try:
        # Query the genie_chat_history
        query = """
            SELECT id, datetime, question, answer, genie_users_id, team_id_slack, user_id_slack,
                   company_id, is_answered, db_schema, resourcename, ai_engine, results_len,
                   score, ai_response, intermediate_steps, chart_code, total_tokens, total_cost, question_hash, total_time, db_warehouse,
                   ai_model, ai_temp, chart_image_url, client_type, results_s3_key
            FROM genie_chat_history 
            WHERE genie_users_id = %s
            AND question_hash = %s
            --AND answer IS NOT NULL
            --AND datetime BETWEEN NOW() - INTERVAL '10 minutes' AND NOW()
            ORDER BY datetime DESC 
            LIMIT 1;
        """
        cur.execute(query, (genie_users_id, question_hash))
        results = cur.fetchall()

        history = []
        for result in results:
            history_entry = {
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
                "score": result[13],
                "ai_response": result[14],
                "intermediate_steps": result[15],
                "chart_code": result[16],
                "total_tokens": result[17],
                "total_cost": result[18],
                "question_hash": result[19],
                "total_time": result[20],
                "db_warehouse": result[21],
                "ai_model": result[22],
                "ai_temp": result[23],
                "chart_image_url": result[24],
                "client_type": result[25],
                "results_s3_key": result[26],
            }
            history.append(history_entry)

        return history
    except Exception as e:
        traceback.print_exc()
        print(f"get_history_by_question_hash, Database error: {e}")
        return None
    finally:
        cur.close()
        conn.close()


def count_history_by_question_hash_count(conn, genie_users_id, question_hash, resourcename, db_schema="",
                                         db_warehouse=""):
    cur = conn.cursor()

    # Handle null values for db_schema and db_warehouse
    if not db_schema:
        db_schema = ""
    if not db_warehouse:
        db_warehouse = ""

    try:
        # Query to count the entries
        query = """
            SELECT COUNT(*)
            FROM genie_chat_history
            WHERE 
                genie_users_id = %s AND 
                question_hash = %s AND 
                resourcename = %s AND 
                db_schema = %s AND 
                db_warehouse = %s
        """
        cur.execute(query,
                    (genie_users_id, question_hash, resourcename, db_schema, db_warehouse))
        count = cur.fetchone()[0]

        return count
    except Exception as e:
        traceback.print_exc()
        print(f"count_history_by_question_hash_count, Database error: {e}")
        return None
    finally:
        cur.close()
        conn.close()


def list_history_by_question_hash(
        conn, genie_users_id, question_hash, resourcename, db_schema="", db_warehouse="",
        limit=10, skip=0
):
    cur = conn.cursor()

    # Handle null values for db_schema and db_warehouse
    if not db_schema:
        db_schema = ""
    if not db_warehouse:
        db_warehouse = ""

    try:
        # Query to select all fields
        query = """
            SELECT id, datetime, question, answer, genie_users_id, team_id_slack, user_id_slack,
                   company_id, is_answered, db_schema, resourcename, ai_engine, results_len,
                   score, ai_response, intermediate_steps, chart_code, total_tokens, total_cost, question_hash, total_time, db_warehouse,
                   ai_model, ai_temp, chart_image_url, client_type, results_s3_key
            FROM genie_chat_history
            WHERE 
                genie_users_id = %s AND 
                question_hash = %s AND 
                resourcename = %s AND 
                db_schema = %s AND 
                db_warehouse = %s
            ORDER BY 
                datetime DESC 
            LIMIT %s OFFSET %s;
        """
        cur.execute(query, (
            genie_users_id, question_hash, resourcename,
            db_schema, db_warehouse,
            limit, skip,
        ))
        results = cur.fetchall()

        history = []
        for result in results:
            history_entry = {
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
                "score": result[13],
                "ai_response": result[14],
                "intermediate_steps": result[15],
                "chart_code": result[16],
                "total_tokens": result[17],
                "total_cost": result[18],
                "question_hash": result[19],
                "total_time": result[20],
                "db_warehouse": result[21],
                "ai_model": result[22],
                "ai_temp": result[23],
                "chart_image_url": result[24],
                "client_type": result[25],
                "results_s3_key": result[26],
            }
            history.append(history_entry)

        return history
    except Exception as e:
        traceback.print_exc()
        print(f"list_history_by_question_hash, Database error: {e}")
        return None
    finally:
        cur.close()
        conn.close()


def update_history_chart_image_url(conn, id, chart_image_url):
    print(f"update_history_chart_image_url, id={id}, chart_image_url={len(chart_image_url)}")
    cur = conn.cursor()
    try:
        # Update existing record
        update = sql.SQL(
            """
            UPDATE genie_chat_history
            SET chart_image_url=%s
            WHERE id=%s
            """
        )
        values = (chart_image_url, id)
        cur.execute(update, values)
        return True

    except Exception as e:
        print(f"update_history_chart_image_url, Database error: {e}")
        traceback.print_exc()
        return False
    finally:
        conn.commit()
        cur.close()
        conn.close()


def update_history_status(conn, id, status):
    print(f"update_history_status, id={id}")
    cur = conn.cursor()
    try:
        # Update existing record
        update = sql.SQL(
            """
            UPDATE genie_chat_history
            SET status=%s
            WHERE id=%s
            """
        )
        values = (status, id)
        cur.execute(update, values)
        return True

    except Exception as e:
        traceback.print_exc()
        print(f"update_history_status, Database error: {e}")
        return False
    finally:
        conn.commit()
        cur.close()
        conn.close()


def update_history_with_error(conn, id, error_msg, ai_response, status):
    print(f"update_history_with_error, id={id}")
    cur = conn.cursor()
    try:
        # Update existing record
        update = sql.SQL(
            """
            UPDATE genie_chat_history
            SET error_msg=%s, ai_response=%s, status=%s
            WHERE id=%s
            """
        )
        values = (error_msg, ai_response, status, id)
        cur.execute(update, values)
        return True

    except Exception as e:
        traceback.print_exc()
        print(f"update_history_with_error, Database error: {e}")
        return False
    finally:
        conn.commit()
        cur.close()
        conn.close()


def update_history_with_error_and_stats(conn, id, error_msg, ai_response, status, total_tokens, total_cost, total_time):
    print(f"update_history_with_error_and_stats, id={id}")
    cur = conn.cursor()
    try:
        # Update existing record
        update = sql.SQL(
            """
            UPDATE genie_chat_history
            SET error_msg=%s, ai_response=%s, status=%s, total_tokens=%s, total_cost=%s, total_time=%s
            WHERE id=%s
            """
        )
        values = (error_msg, ai_response, status, total_tokens, total_cost, total_time, id)
        cur.execute(update, values)
        return True

    except Exception as e:
        traceback.print_exc()
        print(f"update_history_with_error_and_stats, Database error: {e}")
        return False
    finally:
        conn.commit()
        cur.close()
        conn.close()


def update_history_with_intermediate_steps(conn, id, intermediate_steps):
    print(f"update_history_with_intermediate_steps, id={id}")
    cur = conn.cursor()
    try:
        # Update existing record
        update = sql.SQL(
            """
            UPDATE genie_chat_history
            SET intermediate_steps=%s
            WHERE id=%s
            """
        )
        values = (intermediate_steps, id)
        cur.execute(update, values)
        return True

    except Exception as e:
        print(f"update_history_with_intermediate_steps, Database error: {e}")
        traceback.print_exc()
        return False
    finally:
        conn.commit()
        cur.close()
        conn.close()


def update_history_results_len(conn, id, results_len):
    print(f"update_history_results_len, id={id}")
    cur = conn.cursor()
    try:
        # Update existing record
        update = sql.SQL(
            """
            UPDATE genie_chat_history
            SET results_len=%s
            WHERE id=%s
            """
        )
        values = (results_len, id)
        cur.execute(update, values)
        return True

    except Exception as e:
        print(f"update_history_results_len, Database error: {e}")
        traceback.print_exc()
        return False
    finally:
        conn.commit()
        cur.close()
        conn.close()


def update_history_chart_data(conn, id, chart_code, chart_image_url):
    print(f"update_history_chart_data, id={id}")
    cur = conn.cursor()
    try:
        # Update existing record
        update = sql.SQL(
            """
            UPDATE genie_chat_history
            SET chart_code=%s, chart_image_url=%s 
            WHERE id=%s
            """
        )
        values = (chart_code, chart_image_url, id)
        cur.execute(update, values)
        return True

    except Exception as e:
        print(f"update_history_chart_data, Database error: {e}")
        traceback.print_exc()
        return False
    finally:
        conn.commit()
        cur.close()
        conn.close()


def update_history_results_s3_key(conn, id, results_s3_key):
    print(f"update_history_results_s3_key, id={id}")
    cur = conn.cursor()
    try:
        # Update existing record
        update = sql.SQL(
            """
            UPDATE genie_chat_history
            SET results_s3_key=%s 
            WHERE id=%s
            """
        )
        values = (results_s3_key, id)
        cur.execute(update, values)
        return True

    except Exception as e:
        print(f"update_history_results_s3_key, Database error: {e}")
        traceback.print_exc()
        return False
    finally:
        conn.commit()
        cur.close()
        conn.close()


def create_or_update_history(conn, question, answer, genie_users_id, team_id_slack, user_id_slack, company_id, id=None,
                             is_answered=False, db_schema="", resourcename="", ai_engine="", results_len=0,
                             score=0, ai_response="", intermediate_steps=None,
                             question_hash="", chart_code="",
                             total_tokens=0, total_cost=0, total_time=0, status=0, db_warehouse="",
                             ai_model=AGENT_LLM_MODEL_CHART,
                             ai_temp=TEMPERATURE,
                             client_type=0,
                             ):
    if intermediate_steps is None:
        intermediate_steps = []
    cur = conn.cursor()

    if db_schema is None:
        db_schema = ""
    if db_warehouse is None:
        db_warehouse = ""

    try:
        now = datetime.datetime.now(tz=pytz.UTC)

        if id:
            print(f"create_or_update_history, UPDATE, id={id}")
            # Update existing record
            update = sql.SQL(
                """
                UPDATE genie_chat_history
                SET datetime=%s, answer=%s, is_answered=%s, results_len=%s, score=%s, ai_response=%s, intermediate_steps=%s, 
                chart_code=%s, total_tokens=%s, total_cost=%s, total_time=%s, status=%s, ai_model=%s, ai_temp=%s, client_type=%s
                WHERE id=%s
                """
            )
            values = (
                now, answer, is_answered, results_len, score, ai_response, intermediate_steps, chart_code, total_tokens,
                total_cost, total_time, status, ai_model, ai_temp, client_type, id)
            cur.execute(update, values)
            return True
        else:
            print(f"create_or_update_history, INSERT")
            # Calculate SHA-256 hash of the question
            # Insert new record
            insert = sql.SQL(
                """
                INSERT INTO genie_chat_history (datetime, question, answer, genie_users_id, team_id_slack, user_id_slack, company_id, is_answered, 
                db_schema, resourcename, ai_engine, results_len, score, question_hash, db_warehouse,
                ai_model, ai_temp, client_type
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
                """
            )
            values = (
                now, question, answer, genie_users_id, team_id_slack, user_id_slack, company_id, is_answered, db_schema,
                resourcename, ai_engine, results_len, score, question_hash, db_warehouse,
                ai_model, ai_temp, client_type
            )
            cur.execute(insert, values)

            # Retrieve and return the generated ID
            generated_id = cur.fetchone()[0]
            return generated_id
    except Exception as e:
        print(f"create_or_update_history, Database error: {e}")
        traceback.print_exc()
        return None
    finally:
        conn.commit()
        cur.close()
        conn.close()


def get_history_by_genie_users_id(conn, genie_users_id, limit=10, skip=0):
    cur = conn.cursor()

    try:
        # Query the genie_chat_history
        query = """
            SELECT id, datetime, question, answer, genie_users_id, team_id_slack, user_id_slack,
            company_id, is_answered, db_schema, resourcename, ai_engine, results_len,
            score, ai_response, intermediate_steps, chart_code, total_tokens, total_cost, question_hash, total_time, db_warehouse,
            ai_model, ai_temp, chart_image_url, client_type, results_s3_key
            FROM genie_chat_history 
            WHERE genie_users_id = %s
            ORDER BY datetime DESC 
            LIMIT %s OFFSET %s
        """
        cur.execute(query, (genie_users_id, limit, skip))
        results = cur.fetchall()

        history = []
        for result in results:
            history_entry = {
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
                "score": result[13],
                "ai_response": result[14],
                "intermediate_steps": result[15],
                "chart_code": result[16],
                "total_tokens": result[17],
                "total_cost": result[18],
                "question_hash": result[19],
                "total_time": result[20],
                "db_warehouse": result[21],
                "ai_model": result[22],
                "ai_temp": result[23],
                "chart_image_url": result[24],
                "client_type": result[25],
                "results_s3_key": result[26],
            }
            history.append(history_entry)

        return history
    except Exception as e:
        traceback.print_exc()
        print(f"get_history_by_genie_users_id, Database error: {e}")
        return None
    finally:
        cur.close()
        conn.close()


def get_history_by_user_and_team(conn, user_id_slack, team_id_slack, resourcename, limit=10, skip=0):
    cur = conn.cursor()

    try:
        # Query the genie_chat_history
        query = """
            SELECT 
                gh.id, 
                gh.datetime, 
                gh.question, 
                gh.answer, 
                gh.genie_users_id, 
                gh.team_id_slack, 
                gh.user_id_slack,
                gh.company_id, 
                gh.is_answered, 
                gh.db_schema, 
                gh.resourcename, 
                gh.ai_engine, 
                gh.results_len, 
                gh.score, 
                gh.ai_response, 
                gh.intermediate_steps, 
                gh.chart_code,
                gh.total_tokens,
                gh.total_cost,
                gh.question_hash,
                gh.total_time,
                gh.db_warehouse,
                gh.ai_model,
                gh.ai_temp,
                gh.chart_image_url,
                gh.client_type,
                gh.results_s3_key 
            FROM 
                genie_chat_history gh
            INNER JOIN (
                SELECT 
                    question_hash, 
                    MAX(datetime) AS latest_datetime
                FROM 
                    genie_chat_history
                WHERE 
                    user_id_slack = %s AND team_id_slack = %s AND resourcename = %s
                GROUP BY 
                    question_hash
            ) latest_questions ON gh.question_hash = latest_questions.question_hash AND gh.datetime = latest_questions.latest_datetime
            WHERE 
                gh.user_id_slack = %s AND gh.team_id_slack = %s AND resourcename = %s
            ORDER BY 
                gh.datetime DESC 
            LIMIT %s OFFSET %s;
        """
        cur.execute(query, (
            user_id_slack, team_id_slack, resourcename, user_id_slack, team_id_slack, resourcename, limit, skip))
        results = cur.fetchall()

        history = []
        for result in results:
            history_entry = {
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
                "score": result[13],
                "ai_response": result[14],
                "intermediate_steps": result[15],
                "chart_code": result[16],
                "total_tokens": result[17],
                "total_cost": result[18],
                "question_hash": result[19],
                "total_time": result[20],
                "db_warehouse": result[21],
                "ai_model": result[22],
                "ai_temp": result[23],
                "chart_image_url": result[24],
                "client_type": result[25],
                "results_s3_key": result[26],
            }
            history.append(history_entry)

        return history
    except Exception as e:
        traceback.print_exc()
        print(f"get_history_by_user_and_team, Database error: {e}")
        return None
    finally:
        cur.close()
        conn.close()


def get_history_company_id(conn, company_id, resourcename, limit=10, skip=0):
    cur = conn.cursor()

    try:
        # Query the genie_chat_history
        query = """
            SELECT 
                gh.id, 
                gh.datetime, 
                gh.question, 
                gh.answer, 
                gh.genie_users_id, 
                gh.team_id_slack, 
                gh.user_id_slack,
                gh.company_id, 
                gh.is_answered, 
                gh.db_schema, 
                gh.resourcename, 
                gh.ai_engine, 
                gh.results_len, 
                gh.score, 
                gh.ai_response, 
                gh.intermediate_steps, 
                gh.chart_code,
                gh.total_tokens,
                gh.total_cost,
                gh.question_hash,
                gh.total_time,
                gh.db_warehouse,
                gh.ai_model,
                gh.ai_temp,
                gh.chart_image_url,
                gh.client_type,
                gh.results_s3_key 
            FROM 
                genie_chat_history gh
            INNER JOIN (
                SELECT 
                    question_hash, 
                    MAX(datetime) AS latest_datetime
                FROM 
                    genie_chat_history
                WHERE 
                    company_id = %s AND resourcename = %s
                GROUP BY 
                    question_hash
            ) latest_questions ON gh.question_hash = latest_questions.question_hash AND gh.datetime = latest_questions.latest_datetime
            WHERE 
                gh.company_id = %s AND gh.resourcename = %s
            ORDER BY 
                gh.datetime DESC 
            LIMIT %s OFFSET %s;
        """
        cur.execute(query, (company_id, resourcename, company_id, resourcename, limit, skip))
        results = cur.fetchall()

        history = []
        for result in results:
            history_entry = {
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
                "score": result[13],
                "ai_response": result[14],
                "intermediate_steps": result[15],
                "chart_code": result[16],
                "total_tokens": result[17],
                "total_cost": result[18],
                "question_hash": result[19],
                "total_time": result[20],
                "db_warehouse": result[21],
                "ai_model": result[22],
                "ai_temp": result[23],
                "chart_image_url": result[24],
                "client_type": result[25],
                "results_s3_key": result[26],
            }
            history.append(history_entry)

        return history
    except Exception as e:
        traceback.print_exc()
        print(f"get_history_company_id, Database error: {e}")
        return None
    finally:
        cur.close()
        conn.close()


def get_history_by_user_id_skip_limit(
        conn,
        genie_users_id,
        resourcename,
        limit=10,
        skip=0
):
    cur = conn.cursor()

    try:
        # Query the genie_chat_history
        query = """
            SELECT 
                gh.id, 
                gh.datetime, 
                gh.question, 
                gh.answer, 
                gh.genie_users_id, 
                gh.team_id_slack, 
                gh.user_id_slack,
                gh.company_id, 
                gh.is_answered, 
                gh.db_schema, 
                gh.resourcename, 
                gh.ai_engine, 
                gh.results_len, 
                gh.score, 
                gh.ai_response, 
                gh.intermediate_steps, 
                gh.chart_code,
                gh.total_tokens,
                gh.total_cost,
                gh.question_hash,
                gh.total_time,
                gh.db_warehouse,
                gh.ai_model,
                gh.ai_temp,
                gh.chart_image_url,
                gh.client_type,
                gh.results_s3_key,
                gh.error_msg,
                gh.status
            FROM 
                genie_chat_history gh
            INNER JOIN (
                SELECT 
                    question_hash, 
                    MAX(datetime) AS latest_datetime
                FROM 
                    genie_chat_history
                WHERE 
                    genie_users_id = %s AND resourcename = %s
                GROUP BY 
                    question_hash
            ) latest_questions ON gh.question_hash = latest_questions.question_hash AND gh.datetime = latest_questions.latest_datetime
            WHERE 
                gh.genie_users_id = %s AND 
                gh.resourcename = %s
            ORDER BY 
                gh.datetime DESC 
            LIMIT %s OFFSET %s;
        """
        cur.execute(query, (genie_users_id, resourcename, genie_users_id, resourcename, limit, skip))
        results = cur.fetchall()

        history = []
        for result in results:
            history_entry = {
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
                "score": result[13],
                "ai_response": result[14],
                "intermediate_steps": result[15],
                "chart_code": result[16],
                "total_tokens": result[17],
                "total_cost": result[18],
                "question_hash": result[19],
                "total_time": result[20],
                "db_warehouse": result[21],
                "ai_model": result[22],
                "ai_temp": result[23],
                "chart_image_url": result[24],
                "client_type": result[25],
                "results_s3_key": result[26],
                "error_msg": result[27],
                "status": result[28],
            }
            history.append(history_entry)

        return history
    except Exception as e:
        traceback.print_exc()
        print(f"get_history_by_user_id_skip_limit, Database error: {e}")
        return None
    finally:
        cur.close()
        conn.close()


def get_history_by_user_id_schema_warehouse_skip_limit(
        conn,
        genie_users_id,
        resourcename,
        db_schema="",
        db_warehouse="",
        limit=10,
        skip=0,

):
    cur = conn.cursor()

    if not db_schema:
        db_schema = ""
    if not db_warehouse:
        db_warehouse = ""

    try:
        # Query the genie_chat_history
        query = """
            SELECT 
                gh.id, 
                gh.datetime, 
                gh.question, 
                gh.answer, 
                gh.genie_users_id, 
                gh.team_id_slack, 
                gh.user_id_slack,
                gh.company_id, 
                gh.is_answered, 
                gh.db_schema, 
                gh.resourcename, 
                gh.ai_engine, 
                gh.results_len, 
                gh.score, 
                gh.ai_response, 
                gh.intermediate_steps, 
                gh.chart_code,
                gh.total_tokens,
                gh.total_cost,
                gh.question_hash,
                gh.total_time,
                gh.db_warehouse,
                gh.ai_model,
                gh.ai_temp,
                gh.chart_image_url,
                gh.client_type,
                gh.results_s3_key,
                gh.error_msg,
                gh.status
            FROM 
                genie_chat_history gh
            INNER JOIN (
                SELECT 
                    question_hash, 
                    MAX(datetime) AS latest_datetime
                FROM 
                    genie_chat_history
                WHERE 
                    genie_users_id = %s AND 
                    resourcename = %s AND
                    db_schema = %s AND   
                    db_warehouse = %s 
                GROUP BY 
                    question_hash
            ) latest_questions ON gh.question_hash = latest_questions.question_hash AND gh.datetime = latest_questions.latest_datetime
            WHERE 
                gh.genie_users_id = %s AND 
                gh.resourcename = %s AND
                gh.db_schema = %s AND   
                gh.db_warehouse = %s 
            ORDER BY 
                gh.datetime DESC 
            LIMIT %s OFFSET %s;
        """
        cur.execute(query,
                    (
                        genie_users_id, resourcename, db_schema, db_warehouse,
                        genie_users_id, resourcename, db_schema, db_warehouse,
                        limit, skip
                    ))
        results = cur.fetchall()

        history = []
        for result in results:
            history_entry = {
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
                "score": result[13],
                "ai_response": result[14],
                "intermediate_steps": result[15],
                "chart_code": result[16],
                "total_tokens": result[17],
                "total_cost": result[18],
                "question_hash": result[19],
                "total_time": result[20],
                "db_warehouse": result[21],
                "ai_model": result[22],
                "ai_temp": result[23],
                "chart_image_url": result[24],
                "client_type": result[25],
                "results_s3_key": result[26],
                "error_msg": result[27],
                "status": result[28],
            }
            history.append(history_entry)

        return history
    except Exception as e:
        traceback.print_exc()
        print(f"get_history_by_user_id_schema_warehouse_skip_limit, Database error: {e}")
        return None
    finally:
        cur.close()
        conn.close()


def get_history_by_team_id_user_id_company_id_skip_limit(conn, slack_team_id, slack_user_id, company_id, resourcename,
                                                         limit=10,
                                                         skip=0):
    cur = conn.cursor()

    try:
        # Query the genie_chat_history
        query = """
            SELECT 
                gh.id, 
                gh.datetime, 
                gh.question, 
                gh.answer, 
                gh.genie_users_id, 
                gh.team_id_slack, 
                gh.user_id_slack,
                gh.company_id, 
                gh.is_answered, 
                gh.db_schema, 
                gh.resourcename, 
                gh.ai_engine, 
                gh.results_len,
                gh.score, 
                gh.ai_response, 
                gh.intermediate_steps, 
                gh.chart_code,
                gh.total_tokens,
                gh.total_cost,
                gh.question_hash,
                gh.total_time,
                gh.db_warehouse,
                gh.ai_model,
                gh.ai_temp,
                gh.chart_image_url,
                gh.client_type,
                gh.results_s3_key
            FROM 
                genie_chat_history gh
            INNER JOIN (
                SELECT 
                    question_hash, 
                    MAX(datetime) AS latest_datetime
                FROM 
                    genie_chat_history
                WHERE 
                    user_id_slack = %s AND team_id_slack = %s AND company_id = %s AND resourcename = %s AND answer IS NOT NULL AND results_len > 0
                GROUP BY 
                    question_hash
            ) latest_questions ON gh.question_hash = latest_questions.question_hash AND gh.datetime = latest_questions.latest_datetime
            WHERE 
                gh.user_id_slack = %s AND gh.team_id_slack = %s AND gh.company_id = %s AND gh.resourcename = %s
            ORDER BY 
                gh.datetime DESC 
            LIMIT %s OFFSET %s;
        """
        cur.execute(query,
                    (slack_user_id, slack_team_id, company_id, resourcename, slack_user_id, slack_team_id, company_id,
                     resourcename, limit, skip))
        results = cur.fetchall()

        history = []
        for result in results:
            history_entry = {
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
                "score": result[13],
                "ai_response": result[14],
                "intermediate_steps": result[15],
                "chart_code": result[16],
                "total_tokens": result[17],
                "total_cost": result[18],
                "question_hash": result[19],
                "total_time": result[20],
                "db_warehouse": result[21],
                "ai_model": result[22],
                "ai_temp": result[23],
                "chart_image_url": result[24],
                "client_type": result[25],
                "results_s3_key": result[26],
            }
            history.append(history_entry)

        return history
    except Exception as e:
        traceback.print_exc()
        print(f"get_history_by_team_id_user_id_company_id_skip_limit, Database error: {e}")
        return None
    finally:
        cur.close()
        conn.close()


def get_history_by_client_type_skip_limit(
        conn,
        genie_users_id,
        company_id,
        resourcename,
        db_schema,
        db_warehouse,
        client_type,
        limit=10,
        skip=0
):
    cur = conn.cursor()

    if not db_schema:
        db_schema = ""
    if not db_warehouse:
        db_warehouse = ""

    print(
        f"get_history_by_client_type_skip_limit, genie_users_id={genie_users_id}, company_id={company_id}, client_type={client_type}, resourcename={resourcename}, db_schema={db_schema}, db_warehouse={db_warehouse}", )

    try:
        # Query the genie_chat_history
        query = """
            SELECT 
                gh.id, 
                gh.datetime, 
                gh.question, 
                gh.answer, 
                gh.genie_users_id, 
                gh.team_id_slack, 
                gh.user_id_slack,
                gh.company_id, 
                gh.is_answered, 
                gh.db_schema, 
                gh.resourcename, 
                gh.ai_engine, 
                gh.results_len,
                gh.score, 
                gh.ai_response, 
                gh.intermediate_steps, 
                gh.chart_code,
                gh.total_tokens,
                gh.total_cost,
                gh.question_hash,
                gh.total_time,
                gh.db_warehouse,
                gh.ai_model,
                gh.ai_temp,
                gh.chart_image_url,
                gh.client_type,
                gh.results_s3_key
            FROM 
                genie_chat_history gh
            INNER JOIN (
                SELECT 
                    question_hash, 
                    MAX(datetime) AS latest_datetime 
                FROM 
                    genie_chat_history 
                WHERE 
                    genie_users_id = %s 
                    AND company_id = %s 
                    AND client_type = %s 
                    AND resourcename = %s 
                    AND db_schema = %s 
                    AND db_warehouse = %s 
                    AND answer IS NOT NULL 
                    AND results_len > 0
                GROUP BY 
                    question_hash
            ) latest_questions ON gh.question_hash = latest_questions.question_hash AND gh.datetime = latest_questions.latest_datetime
            WHERE 
                gh.genie_users_id = %s 
                AND gh.company_id = %s 
                AND gh.client_type = %s 
                AND gh.resourcename = %s
                AND gh.db_schema = %s  
                AND gh.db_warehouse = %s 
            ORDER BY 
                gh.datetime DESC 
            LIMIT %s OFFSET %s;
        """
        cur.execute(query,
                    (genie_users_id, company_id, client_type, resourcename, db_schema, db_warehouse,

                     genie_users_id, company_id, client_type, resourcename, db_schema, db_warehouse,
                     limit, skip)
                    )
        results = cur.fetchall()

        history = []
        for result in results:
            history_entry = {
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
                "score": result[13],
                "ai_response": result[14],
                "intermediate_steps": result[15],
                "chart_code": result[16],
                "total_tokens": result[17],
                "total_cost": result[18],
                "question_hash": result[19],
                "total_time": result[20],
                "db_warehouse": result[21],
                "ai_model": result[22],
                "ai_temp": result[23],
                "chart_image_url": result[24],
                "client_type": result[25],
                "results_s3_key": result[26],
            }
            history.append(history_entry)

        return history
    except Exception as e:
        traceback.print_exc()
        print(f"get_history_by_client_type_skip_limit, Database error: {e}")
        return None
    finally:
        cur.close()
        conn.close()


def get_history_by_id(conn, company_id, id):
    cur = conn.cursor()

    try:
        # Query the genie_chat_history
        query = """
            SELECT id, datetime, question, answer, genie_users_id, team_id_slack, user_id_slack,
            company_id, is_answered, db_schema, resourcename, ai_engine, results_len,
            score, ai_response, intermediate_steps, chart_code, total_tokens, total_cost, question_hash, total_time,
            status, table_name, db_warehouse, ai_model, ai_temp, chart_image_url, client_type, results_s3_key
            FROM genie_chat_history 
            WHERE company_id = %s
            AND id = %s            
        """
        cur.execute(query, (company_id, id))
        results = cur.fetchall()

        history = []
        for result in results:
            history_entry = {
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
                "score": result[13],
                "ai_response": result[14],
                "intermediate_steps": result[15],
                "chart_code": result[16],
                "total_tokens": result[17],
                "total_cost": result[18],
                "question_hash": result[19],
                "total_time": result[20],
                "status": result[21],
                "table_name": result[22],
                "db_warehouse": result[23],
                "ai_model": result[24],
                "ai_temp": result[25],
                "chart_image_url": result[26],
                "client_type": result[27],
                "results_s3_key": result[28],
            }
            history.append(history_entry)

        return history
    except Exception as e:
        traceback.print_exc()
        print(f"get_history_by_id, Database error: {e}")
        return None
    finally:
        cur.close()
        conn.close()


def get_chat_history_count_by_genie_users_id(conn, genie_users_id, year=None, month=None):
    from datetime import datetime

    cur = conn.cursor()

    # If year and month are not provided, use current year and month
    if year is None or month is None:
        today = datetime.now()
        year = today.year
        month = today.month

    # Calculate the first and last day of the given month
    first_day = datetime(year, month, 1)
    last_day = datetime(year, month, calendar.monthrange(year, month)[1], 23, 59, 59)

    try:
        # Query to count the requests
        query = """
            SELECT COUNT(*)
            FROM genie_chat_history 
            WHERE genie_users_id = %s AND datetime BETWEEN %s AND %s
        """
        cur.execute(query, (genie_users_id, first_day, last_day))
        result = cur.fetchone()

        request_count = result[0] if result else 0
        return request_count
    except Exception as e:
        traceback.print_exc()
        print(f"get_chat_history_count_by_genie_users_id, Database error: {e}")
        return None
    finally:
        cur.close()
        conn.close()


def get_chat_history_count_by_company_id(conn, company_id, year=None, month=None):
    from datetime import datetime

    cur = conn.cursor()

    # If year and month are not provided, use current year and month
    if year is None or month is None:
        today = datetime.now()
        year = today.year
        month = today.month

    # Calculate the first and last day of the given month
    first_day = datetime(year, month, 1)
    last_day = datetime(year, month, calendar.monthrange(year, month)[1], 23, 59, 59)

    try:
        # Query to count the requests
        query = """
            SELECT COUNT(*)
            FROM genie_chat_history 
            WHERE company_id = %s AND datetime BETWEEN %s AND %s
        """
        cur.execute(query, (company_id, first_day, last_day))
        result = cur.fetchone()

        request_count = result[0] if result else 0
        return request_count
    except Exception as e:
        traceback.print_exc()
        print(f"get_chat_history_count_by_company_id, Database error: {e}")
        return None
    finally:
        cur.close()
        conn.close()


def get_chat_history_list_by_company_id(conn, company_id, year=None, month=None):
    from datetime import datetime

    cur = conn.cursor()

    # If year and month are not provided, use current year and month
    if year is None or month is None:
        today = datetime.now()
        year = today.year
        month = today.month

    # Calculate the first and last day of the given month
    first_day = datetime(year, month, 1)
    last_day = datetime(year, month, calendar.monthrange(year, month)[1], 23, 59, 59)

    try:
        # Query to count the requests
        query = """
            SELECT id, datetime, question, answer, genie_users_id, team_id_slack, user_id_slack,
            company_id, is_answered, db_schema, resourcename, ai_engine, results_len,
            score, ai_response, intermediate_steps, chart_code, total_tokens, total_cost, question_hash, total_time,
            status, table_name, db_warehouse, ai_model, ai_temp, chart_image_url, client_type, results_s3_key
            FROM genie_chat_history 
            WHERE company_id = %s AND datetime BETWEEN %s AND %s
        """

        cur.execute(query, (company_id, first_day, last_day))
        results = cur.fetchall()

        history = []
        for result in results:
            history_entry = {
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
                "score": result[13],
                "ai_response": result[14],
                "intermediate_steps": result[15],
                "chart_code": result[16],
                "total_tokens": result[17],
                "total_cost": result[18],
                "question_hash": result[19],
                "total_time": result[20],
                "status": result[21],
                "table_name": result[22],
                "db_warehouse": result[23],
                "ai_model": result[24],
                "ai_temp": result[25],
                "chart_image_url": result[26],
                "client_type": result[27],
                "results_s3_key": result[28],
            }
            history.append(history_entry)

        return history
    except Exception as e:
        traceback.print_exc()
        print(f"get_chat_history_list_by_company_id, Database error: {e}")
        return None
    finally:
        cur.close()
        conn.close()
