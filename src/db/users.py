from psycopg2 import sql, Error


def get_user_by_slack_ids(conn, team_id_slack, user_id_slack):
    cur = conn.cursor()

    # Query to get genie_users based on user_id
    select = sql.SQL(
        """
        SELECT u.id, u.username, u.datetime, u.company_id, u.role, u.stripe_customer_id
        FROM genie_users u
        WHERE u.team_id_slack = %s AND u.user_id_slack = %s
        """
    )

    values = (team_id_slack, user_id_slack)

    try:
        cur.execute(select, values)
        user = cur.fetchone()

        if user:
            user_data = {
                "id": user[0],
                "username": user[1],
                "datetime": user[2],
                "company_id": user[3],
                "role": user[4],
                "stripe_customer_id": user[5],
            }
            return user_data
        else:
            return None

    except Error as e:
        print(f"get_user_by_slack_ids, Database error: {e}")
        return None
    finally:
        cur.close()
        conn.close()
