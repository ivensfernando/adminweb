import calendar
import datetime
import stripe

import pytz
from psycopg2 import sql, Error
from src.utils.func_utils import timestamp_to_date


def update_status_genie_users_payments_by_payment_intent(conn, payment_intent, status):
    cur = conn.cursor()
    try:
        # First, check if a record exists with the provided payment_intent
        select = sql.SQL(
            "SELECT id, genie_users_id FROM genie_users_payments WHERE payment_intent = %s ORDER BY datetime DESC"
        )
        select_values = (payment_intent,)
        cur.execute(select, select_values)

        # Fetch result of the select statement
        result = cur.fetchone()

        if result:
            id = result[0]
            genie_users_id = result[1]
            print(f"insert_or_update_genie_users_payments, result={result}, update")
            update = sql.SQL(
                "UPDATE genie_users_payments SET status = %s WHERE id = %s"
            )
            values = (status, id)

            cur.execute(update, values)
            return genie_users_id
        else:
            #
            print(f"insert_or_update_genie_users_payments, COULD NOT FIND ANY DATA!! ")
            return None
    except Error as e:
        print(f"update_status_genie_users_payments, Database error: {e}")
        return None
    finally:
        conn.commit()
        cur.close()
        conn.close()



def update_status_genie_users_payments_by_subscription_id(
        conn,
        subscription_id,
        status,
        subscription_start_date,
        subscription_status,
        subscription_current_period_start_date,
        subscription_current_period_end_date,
):
    cur = conn.cursor()
    try:
        # First, check if a record exists with the provided payment_intent
        select = sql.SQL(
            "SELECT id, genie_users_id FROM genie_users_payments WHERE subscription_id = %s ORDER BY datetime DESC"
        )
        select_values = (subscription_id,)
        cur.execute(select, select_values)

        # Fetch result of the select statement
        result = cur.fetchone()

        if result:
            id = result[0]
            genie_users_id = result[1]
            print(f"insert_or_update_genie_users_payments, result={result}, update")
            update = sql.SQL(
                """
                UPDATE genie_users_payments 
                    SET status=%s, 
                        subscription_start_date=%s, 
                        subscription_status=%s, 
                        subscription_current_period_start_date=%s, 
                        subscription_current_period_end_date=%s 
                WHERE id = %s
                """
            )
            values = (
                status,
                subscription_start_date,
                subscription_status,
                subscription_current_period_start_date,
                subscription_current_period_end_date,
                id
            )

            cur.execute(update, values)
            return genie_users_id
        else:
            #
            print(f"insert_or_update_genie_users_payments, COULD NOT FIND ANY DATA!! ")
            return None
    except Error as e:
        print(f"update_status_genie_users_payments, Database error: {e}")
        return None
    finally:
        conn.commit()
        cur.close()
        conn.close()


def insert_or_update_genie_users_payments(conn, genie_users_id, genie_payment_plan_id, payment_intent, client_secret,
                                          provider, status, company_id):
    cur = conn.cursor()

    # First, check if a record exists with the provided payment_intent
    select = sql.SQL(
        "SELECT * FROM genie_users_payments WHERE payment_intent = %s"
    )
    select_values = (payment_intent,)
    cur.execute(select, select_values)

    # Fetch result of the select statement
    result = cur.fetchone()
    now = datetime.datetime.now(tz=pytz.UTC)

    if result:
        print(f"insert_or_update_genie_users_payments, found payment_intent, result={result}")
        # If a record exists, perform an update
        update = sql.SQL(
            "UPDATE genie_users_payments SET genie_users_id = %s, genie_payment_plan_id = %s, client_secret = %s, provider = %s, status = %s, datetime = %s, company_id = %s WHERE payment_intent = %s"
        )
        values = (
            genie_users_id, genie_payment_plan_id, client_secret, provider, status, now, payment_intent, company_id)

        cur.execute(update, values)
    else:
        # If no record exists, perform an insert
        insert = sql.SQL(
            "INSERT INTO genie_users_payments (genie_users_id, genie_payment_plan_id, payment_intent, client_secret, provider, datetime, status, company_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        )
        values = (
            genie_users_id, genie_payment_plan_id, payment_intent, client_secret, provider, now, status, company_id)

        cur.execute(insert, values)

    conn.commit()
    cur.close()
    conn.close()


def insert_or_update_genie_users_payments_by_subscription_id(
        conn, genie_users_id, genie_payment_plan_id,
        subscription_id, client_secret,
        provider, status, company_id,
        subscription_item_id
):
    cur = conn.cursor()

    # First, check if a record exists with the provided subscription_id
    select = sql.SQL(
        "SELECT id FROM genie_users_payments WHERE subscription_id = %s ORDER BY datetime DESC"
    )
    select_values = (subscription_id,)
    cur.execute(select, select_values)

    # Fetch result of the select statement
    result = cur.fetchone()
    now = datetime.datetime.now(tz=pytz.UTC)

    if result:
        id = result["id"]
        print(f"insert_or_update_genie_users_payments, found payment_intent, result={result}")
        # If a record exists, perform an update
        update = sql.SQL(
            """
            UPDATE genie_users_payments 
                SET genie_users_id = %s, 
                    genie_payment_plan_id = %s, 
                    client_secret = %s, 
                    provider = %s, 
                    status = %s, 
                    datetime = %s, 
                    company_id = %s,
                    subscription_item_id = %s 
                WHERE id = %s
            """
        )
        values = (
            genie_users_id, genie_payment_plan_id, client_secret, provider, status, now, company_id, subscription_item_id, id)

        cur.execute(update, values)
    else:
        # If no record exists, perform an insert
        insert = sql.SQL(
            "INSERT INTO genie_users_payments (genie_users_id, genie_payment_plan_id, subscription_id, client_secret, provider, datetime, status, company_id, subscription_item_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        values = (
            genie_users_id, genie_payment_plan_id, subscription_id, client_secret, provider, now, status, company_id, subscription_item_id)

        cur.execute(insert, values)

    conn.commit()
    cur.close()
    conn.close()





def update_subscription_item_id_by_subscription_id(
        conn, subscription_id, subscription_item_id
):
    cur = conn.cursor()

    print(f"update_subscription_item_id_by_subscription_id, subscription_id={subscription_id}")
    # If a record exists, perform an update
    update = sql.SQL(
        """
        UPDATE genie_users_payments 
            SET subscription_item_id = %s 
        WHERE id = %s
        """
    )
    values = (subscription_item_id, subscription_id)

    cur.execute(update, values)

    conn.commit()
    cur.close()
    conn.close()



def get_genie_payment_plan(conn, id):
    cur = conn.cursor()

    # Check user credentials
    select = sql.SQL(
        "SELECT id, plan, description, amount, datetime, stripe_price_id FROM genie_payment_plan WHERE stripe_price_id = %s"
    )

    values = (id,)

    try:
        cur.execute(select, values)
        plan = cur.fetchone()

        if plan:
            return {
                "id": plan[0],
                "plan": plan[1],
                "description": plan[2],
                "amount": plan[3],
                "datetime": plan[4],
                "stripe_price_id": plan[5],
            }
        else:
            return None
    except Error as e:
        print(f"get_genie_payment_plan, Database error: {e}")
        return None
    finally:
        cur.close()
        conn.close()


def get_genie_payment_history(conn, id):
    cur = conn.cursor()

    # Check user credentials
    select = sql.SQL(
        """
        SELECT gup.id, gup.provider, gup.genie_payment_plan_id, gup.status, gup.datetime, gup.genie_users_id, gpp.amount
        FROM genie_users_payments AS gup 
        JOIN genie_payment_plan AS gpp ON gup.genie_payment_plan_id = gpp.id 
        WHERE gup.genie_users_id = %s 
        ORDER BY gup.datetime DESC
        """
    )

    values = (id,)

    try:
        cur.execute(select, values)
        results = cur.fetchall()

        if results:
            genie_users_payments = []
            for result in results:
                genie_users_payment = {
                    "id": result[0],
                    "provider": result[1],
                    "genie_payment_plan_id": result[2],
                    "status": result[3],
                    "datetime": result[4],
                    "genie_users_id": result[5],
                    "amount": result[6],
                }
                genie_users_payments.append(genie_users_payment)
            return genie_users_payments
        else:
            return None
    except Error as e:
        print(f"get_genie_payment_history, Database error: {e}")
        return None
    finally:
        cur.close()
        conn.close()


def get_genie_users_payments_by_genie_users_id(conn, genie_users_id):
    cur = conn.cursor()
    try:
        # Query to join genie_users_payments with genie_payment_plan
        select = sql.SQL(
            """
            SELECT 
                p.id, 
                p.genie_users_id, 
                p.status, 
                p.genie_payment_plan_id,
                p.subscription_id,
                p.datetime,
                p.subscription_start_date,
                p.subscription_status,
                p.subscription_current_period_start_date,
                p.subscription_current_period_end_date,
                p.subscription_item_id,
                pl.plan,
                pl.amount,
                pl.stripe_price_id
            FROM 
                genie_users_payments p
            INNER JOIN 
                genie_payment_plan pl ON p.genie_payment_plan_id = pl.id
            WHERE 
                p.genie_users_id = %s
            ORDER BY 
                p.datetime DESC
            """
        )
        select_values = (genie_users_id,)
        cur.execute(select, select_values)

        # Fetch result of the select statement
        result = cur.fetchone()

        if result:
            payment_details = {
                "id": result[0],
                "genie_users_id": result[1],
                "status": result[2],
                "genie_payment_plan_id": result[3],
                "subscription_id": result[4],
                "datetime": result[5],
                "subscription_start_date": result[6],
                "subscription_status": result[7],
                "subscription_current_period_start_date": result[8],
                "subscription_current_period_end_date": result[9],
                "subscription_item_id": result[10],
                "plan": result[11],
                "amount": result[12],
                "stripe_price_id": result[13]
            }
            return payment_details
        else:
            print(f"get_genie_users_payments_by_genie_users_id, COULD NOT FIND ANY DATA!! ")
            return None
    except Error as e:
        print(f"get_genie_users_payments_by_genie_users_id, Database error: {e}")
        return None
    finally:
        conn.commit()
        cur.close()
        conn.close()


def get_genie_users_payments_by_genie_users_id_with_period(conn, genie_users_id, year=None, month=None):
    cur = conn.cursor()
    from datetime import datetime

    # If year and month are not provided, use current year and month
    if year is None or month is None:
        today = datetime.now()
        year = today.year
        month = today.month

    # Calculate the first and last day of the given month
    first_day = datetime(year, month, 1)
    last_day = datetime(year, month, calendar.monthrange(year, month)[1], 23, 59, 59)

    try:
        # Query to join genie_users_payments with genie_payment_plan
        select = sql.SQL(
            """
            SELECT 
                p.id, 
                p.genie_users_id, 
                p.status, 
                p.genie_payment_plan_id,
                p.subscription_id,
                p.datetime,
                pl.plan,
                pl.amount,
                pl.stripe_price_id
            FROM 
                genie_users_payments p
            INNER JOIN 
                genie_payment_plan pl ON p.genie_payment_plan_id = pl.id
            WHERE 
                p.genie_users_id = %s AND p.datetime BETWEEN %s AND %s

            """
        )
        select_values = (genie_users_id, first_day, last_day)
        cur.execute(select, select_values)

        # Fetch result of the select statement
        result = cur.fetchone()

        if result:
            payment_details = {
                "id": result[0],
                "genie_users_id": result[1],
                "status": result[2],
                "genie_payment_plan_id": result[3],
                "subscription_id": result[4],
                "datetime": result[5],
                "plan": result[6],
                "amount": result[7],
                "stripe_price_id": result[8]
            }
            return payment_details
        else:
            print(f"get_genie_users_payments_by_genie_users_id_with_period, COULD NOT FIND ANY DATA!! ")
            return None
    except Error as e:
        print(f"get_genie_users_payments_by_genie_users_id_with_period, Database error: {e}")
        return None
    finally:
        conn.commit()
        cur.close()
        conn.close()


def get_stripe_subscription(subscription_id):
    subscription = stripe.Subscription.retrieve(subscription_id)
    # Subscription start date
    start_date = timestamp_to_date(subscription.created)
    # Current billing period start
    current_period_start = timestamp_to_date(subscription.current_period_start)
    # Current billing period end (next billing date)
    current_period_end = timestamp_to_date(subscription.current_period_end)
    # Print the status of the subscription
    status = subscription.status
    print("Subscription Status:", status)
    print("Subscription Start Date:", start_date)
    print("Current Billing Period Start:", current_period_start)
    print("Next Billing Date:", current_period_end)

    return {
        "subscription_start_date": start_date,
        "subscription_status": status,
        "subscription_current_period_start_date": current_period_start,
        "subscription_current_period_end_date": current_period_end,
    }
