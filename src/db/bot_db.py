import time

import psycopg2

from config.settings.base import BOT_DATABASE_URL


def get_bot_conn(max_retries=10):
    for attempt in range(1, max_retries + 1):
        try:
            conn = psycopg2.connect(BOT_DATABASE_URL)
            return conn
        except Exception as e:
            print(e)
            if attempt < max_retries:
                sleep_time = attempt * 2
                print(f"get_bot_conn, Attempt {attempt} failed. Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                print("get_bot_conn, Reached max retries. Can't connect to db.")
                return None
