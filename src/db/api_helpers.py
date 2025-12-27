from django.contrib.auth.hashers import make_password
from psycopg2 import sql, Error

from config.settings.base import API_KEYS_SECRET_KEY, API_KEYS_SECRET_HASHER
from src.db.utils import generate_api_key


def create_or_update_user_keys(conn, genie_users_id, company_id):
    cur = conn.cursor()
    try:
        # First, check if a record exists with the provided user ID
        select = sql.SQL("SELECT id FROM genie_api_keys WHERE genie_users_id = %s")
        select_values = (genie_users_id,)
        cur.execute(select, select_values)

        # Fetch result of the select statement
        result = cur.fetchone()
        new_key = generate_api_key()  # Generate a new API key
        key_hash = make_password(password=new_key, salt=API_KEYS_SECRET_KEY, hasher=API_KEYS_SECRET_HASHER)

        if result:
            # If a record exists, perform an update
            update = sql.SQL("UPDATE genie_api_keys SET key_hash = %s, key_unsafe = %s WHERE genie_users_id = %s")
            update_values = (key_hash, new_key, genie_users_id)
            cur.execute(update, update_values)
            print(f"create_or_update_user_keys, UPDATE genie_api_keys, genie_users_id={genie_users_id}")
        else:
            # If no record exists, perform an insert
            insert = sql.SQL(
                "INSERT INTO genie_api_keys (key_hash, key_unsafe, usage_limit, usage_count, genie_users_id, allowed_paths, company_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            )
            # Note: You may need to provide default values for `usage_limit`, `usage_count`, and `allowed_paths` or get them from other sources.
            default_usage_limit = 1000
            default_usage_count = 0
            default_allowed_paths = [
                '/api/update/user/database_connection',
                '/api/list/user/database_connection',
                '/api/list/user/database_connection/tables',
                '/api/list/user/database_connection/schemas',
                '/api/isauth',
                '/api/language_to_sql',
                '/api/recommend_questions',
                '/api/predict_questions',
                '/api/get_chat_history',
                "/api/link_app_user_to_company",
                "/api/identify_tables_for_query",
                "/api/get_my_chat_history",
                "/api/language_to_sql_process",
                "/api/list/user/database_connection/warehouses"
            ]  # example paths
            insert_values = (key_hash, new_key, default_usage_limit, default_usage_count, genie_users_id, default_allowed_paths, company_id)
            cur.execute(insert, insert_values)
            print(f"create_or_update_user_keys, INSERT genie_api_keys, genie_users_id={genie_users_id}")

    except Error as e:
        print(f"create_or_update_user_keys, Database error: {e}")
        return None

    finally:
        conn.commit()
        cur.close()
        conn.close()
