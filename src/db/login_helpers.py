import datetime
import secrets
import time
from hashlib import sha256
import traceback

import psycopg2
import pytz
from psycopg2 import sql, Error

from config.settings.base import DATABASE_URL


def getConn(max_retries=10):
    for attempt in range(1, max_retries + 1):
        try:
            conn = psycopg2.connect(DATABASE_URL)
            return conn
        except Exception as e:
            print(e)
            if attempt < max_retries:
                sleep_time = attempt * 2  # increase the sleep time linearly
                print(f"getConn, Attempt {attempt} failed. Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                print("getConn, Reached max retries. Can't connect to db.")
                return None


# Function to create a new user
def create_user(conn, username, password, company_id, role):
    cur = conn.cursor()
    try:
        # Create user
        insert = sql.SQL(
            "INSERT INTO genie_users (username, password, datetime, company_id, role) VALUES (%s, %s, NOW(), %s, %s) RETURNING id"
        )
        pw = sha256(password.encode("utf-8")).hexdigest()
        print(f"create_user, username={username}, pw={pw}")
        values = (username, pw, company_id, role)

        cur.execute(insert, values)
        generated_id = cur.fetchone()[0]

        return generated_id
    except Error as e:
        print(f"create_user, Database error: {e}")
        return False

    finally:
        conn.commit()
        cur.close()
        conn.close()


def get_user_by_email(conn, email):
    cur = conn.cursor()

    try:
        # Query to get genie_users based on user_id
        select = sql.SQL(
            """
            SELECT u.id, u.username, u.datetime, u.company_id, u.role
            FROM genie_users u
            WHERE u.username = %s
            """
        )

        values = (email,)
        cur.execute(select, values)
        user = cur.fetchone()

        if user:
            user_data = {
                "id": user[0],
                "username": user[1],
                "datetime": user[2],
                "company_id": user[3],
                "role": user[4],
            }
            return user_data
        else:
            return None

    except Error as e:
        print(f"get_user_by_email, Database error: {e}")
        traceback.print_exc()
        return None
    finally:
        cur.close()
        conn.close()


def get_user_by_id(conn, id):
    cur = conn.cursor()

    try:
        # Query to get genie_users based on user_id
        select = sql.SQL(
            """
            SELECT u.id, u.username, u.datetime, u.company_id, u.role
            FROM genie_users u
            WHERE u.id = %s
            """
        )

        values = (id,)

        cur.execute(select, values)
        user = cur.fetchone()

        if user:
            user_data = {
                "id": user[0],
                "username": user[1],
                "datetime": user[2],
                "company_id": user[3],
                "role": user[4],
            }
            return user_data
        else:
            return None

    except Error as e:
        print(f"get_user_by_id, Database error: {e}")
        traceback.print_exc()
        return None
    finally:
        cur.close()
        conn.close()


def update_user_password(conn, username, new_password):
    cur = conn.cursor()
    try:
        # Update user password
        update = sql.SQL(
            "UPDATE genie_users SET password=%s WHERE username=%s"
        )

        pw = sha256(new_password.encode("utf-8")).hexdigest()
        print(f"update_user_password, username={username}, new_pw={pw}")
        values = (pw, username)

        cur.execute(update, values)

        # Check how many rows were affected to determine if the update was successful
        updated_rows = cur.rowcount
        if updated_rows == 1:
            return True
        else:
            print(f"update_user_password, No user found with username: {username}")
            return False

    except Error as e:
        traceback.print_exc()
        print(f"update_user_password, Database error: {e}")
        return False

    finally:
        conn.commit()
        cur.close()
        conn.close()


def update_user_role(conn, username, role):
    cur = conn.cursor()
    try:
        # Update user password
        update = sql.SQL(
            "UPDATE genie_users SET role=%s WHERE username=%s"
        )

        print(f"update_user_role, username={username}, role={role}")
        values = (role, username)

        cur.execute(update, values)

        # Check how many rows were affected to determine if the update was successful
        updated_rows = cur.rowcount
        if updated_rows == 1:
            return True
        else:
            print(f"update_user_role, No user found with username: {username}")
            return False

    except Error as e:
        traceback.print_exc()
        print(f"update_user_role, Database error: {e}")
        return False

    finally:
        conn.commit()
        cur.close()
        conn.close()


def update_user_team_id_and_user_id(conn, username, team_id_slack, user_id_slack):
    cur = conn.cursor()
    try:
        # Update user password
        update = sql.SQL(
            "UPDATE genie_users SET team_id_slack=%s, user_id_slack=%s WHERE username=%s"
        )

        print(
            f"update_user_team_id_and_user_id, username={username}, team_id_slack={team_id_slack}, user_id_slack={user_id_slack}")
        values = (team_id_slack, user_id_slack, username)

        cur.execute(update, values)

        # Check how many rows were affected to determine if the update was successful
        updated_rows = cur.rowcount
        if updated_rows == 1:
            return True
        else:
            print(f"update_user_team_id_and_user_id, No user found with username: {username}")
            return False

    except Error as e:
        traceback.print_exc()
        print(f"update_user_team_id_and_user_id, Database error: {e}")
        return False

    finally:
        conn.commit()
        cur.close()
        conn.close()


def delete_user(conn, username):
    cur = conn.cursor()
    try:
        # Update user password
        update = sql.SQL(
            "DELETE FROM genie_users WHERE username=%s"
        )

        print(f"delete_user, username={username}")
        values = (username,)

        cur.execute(update, values)

        # Check how many rows were affected to determine if the update was successful
        updated_rows = cur.rowcount
        if updated_rows == 1:
            return True
        else:
            print(f"delete_user, No user found with username: {username}")
            return False

    except Error as e:
        traceback.print_exc()
        print(f"delete_user, Database error: {e}")
        return False

    finally:
        conn.commit()
        cur.close()
        conn.close()


def update_user_stripe_customer_id(conn, username, stripe_customer_id):
    cur = conn.cursor()
    try:
        # Update stripe_customer_id for the user
        update = sql.SQL(
            "UPDATE genie_users SET stripe_customer_id = %s WHERE username = %s"
        )

        values = (stripe_customer_id, username)

        cur.execute(update, values)
        if cur.rowcount > 0:  # Check if any rows were affected/updated
            return True
        else:
            print(f"update_user_stripe_customer_id, No user with username={username} found.")
            return False
    except Error as e:
        traceback.print_exc()
        print(f"update_user_stripe_customer_id, Database error: {e}")
        return False

    finally:
        conn.commit()
        cur.close()
        conn.close()


# Function to check the user credentials
def login_user(conn, username, password):
    cur = conn.cursor()
    try:
        # Check user credentials
        select = sql.SQL(
            "SELECT id, username, password, stripe_customer_id, company_id, role FROM genie_users WHERE username = %s AND password = %s"
        )
        pw = sha256(password.encode("utf-8")).hexdigest()

        values = (username, pw)

        cur.execute(select, values)
        user = cur.fetchone()

        # Close the connection
        cur.close()
        conn.close()

        if user:
            # Check if the user exists and if the password matches
            id = user[0]
            username = user[1]
            userpw = user[2]
            stripe_customer_id = user[3]
            company_id = user[4]
            role = user[5]

            print(f"login_user, username={username}, stripe_customer_id={stripe_customer_id}")
            if user and pw == userpw:
                # Returns the user info as a dictionary
                return {
                    "id": id,
                    "username": username,
                    "password": userpw,
                    "stripe_customer_id": stripe_customer_id,
                    "company_id": company_id,
                    "role": role,
                }
            else:
                return None
        else:
            return None

    except Exception as e:
        traceback.print_exc()
        print(f"login_user, Database error: {e}")
        return False

    finally:
        cur.close()
        conn.close()


def login_user_with_key(conn, key_hash):
    cur = conn.cursor()
    try:
        # Check user credentials
        select = sql.SQL(
            "SELECT id, key_hash, usage_limit, usage_count, customer_id, allowed_paths FROM api_keys_frontend WHERE key_hash = %s"
        )

        values = (key_hash,)

        cur.execute(select, values)
        user = cur.fetchone()

        if user:
            # Check if the user exists and if the password matches
            key_hash_ret = user[1]

            print(f"login_user_with_key, key_hash_ret={key_hash_ret}")
            if user and key_hash == key_hash_ret:

                update = sql.SQL("UPDATE api_keys_frontend SET usage_count = usage_count + 1 WHERE id = %s;")
                cur.execute(update, (user[0],))
                conn.commit()

                # Close the connection
                cur.close()
                conn.close()
                # Returns the user info as a dictionary
                return {
                    "id": user[0],
                    "user_id": user[0],
                    "key_hash": user[1],
                    "usage_limit": user[2],
                    "usage_count": user[3],
                    "customer_id": user[4],
                    "allowed_paths": user[5]
                }
            else:
                return None
        else:
            return None
    except Exception as e:
        traceback.print_exc()
        print(f"login_user_with_key, Database error: {e}")
        return False

    finally:
        conn.commit()
        cur.close()
        conn.close()


def login_user_with_key_genie(conn, key_hash):
    cur = conn.cursor()
    try:
        print(f"login_user_with_key_genie, SELECT, key_hash={key_hash}")
        # Check user credentials
        select = sql.SQL(
            "SELECT id, key_hash, usage_limit, usage_count, genie_users_id, allowed_paths, company_id FROM genie_api_keys WHERE key_hash = %s;"
        )

        values = (key_hash,)

        cur.execute(select, values)
        user = cur.fetchone()

        if user:
            # Check if the user exists and if the password matches
            key_hash_ret = user[1]
            usage_count = user[3]
            if user and key_hash == key_hash_ret:
                id = user[0]
                print(f"login_user_with_key_genie, UPDATE, id={id}")

                update = sql.SQL("UPDATE genie_api_keys SET usage_count = usage_count + 1 WHERE id = %s;")
                cur.execute(update, (id,))
                conn.commit()
                usage_count = usage_count + 1

                # Returns the user info as a dictionary
                return {
                    "id": user[0],
                    "user_id": user[4],
                    "key_hash": user[1],
                    "usage_limit": user[2],
                    "usage_count": usage_count,
                    "genie_users_id": user[4],
                    "allowed_paths": user[5],
                    "company_id": user[6],
                }
        return None
    except Exception as e:
        traceback.print_exc()
        print(f"login_user_with_key_genie, Database error: {e}")
        return None

    finally:
        cur.close()
        conn.close()


def get_user_key_genie(conn, genie_users_id):
    cur = conn.cursor()
    try:
        # Check user credentials
        select = sql.SQL(
            "SELECT id, key_hash, key_unsafe, usage_limit, usage_count, genie_users_id, allowed_paths, company_id FROM genie_api_keys WHERE genie_users_id = %s"
        )

        values = (genie_users_id,)

        cur.execute(select, values)
        user = cur.fetchone()
        if user:
            # Returns the user info as a dictionary
            return {
                "id": user[0],
                "user_id": user[5],
                "key_hash": user[1],
                "key_unsafe": user[2],
                "usage_limit": user[3],
                "usage_count": user[4],
                "genie_users_id": user[5],
                "allowed_paths": user[6],
                "company_id": user[7],
            }
        else:
            print(f"get_user_key_genie, user not found")
            return None
    except Error as e:
        print(f"get_user_key_genie, Database error: {e}")
        traceback.print_exc()
        return None
    finally:
        cur.close()
        conn.close()



def generate_access_code(length=32):
    return secrets.token_hex(length // 2)  # token_hex returns twice the input length in characters
