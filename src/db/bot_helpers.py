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
                   ue.order_size_percent,
                   ue.weekend_holiday_multiplier,
                   ue.dead_zone_multiplier,
                   ue.asia_multiplier,
                   ue.london_multiplier,
                   ue.us_multiplier,
                   ue.enable_no_trade_window,
                   ue.no_trade_window_orders_closed,
                   ue.strategy_name,
                   ue.symbol,
                   ue.timeframe,
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
                "order_size_percent": row[4],
                "weekend_holiday_multiplier": row[5],
                "dead_zone_multiplier": row[6],
                "asia_multiplier": row[7],
                "london_multiplier": row[8],
                "us_multiplier": row[9],
                "enable_no_trade_window": row[10],
                "no_trade_window_orders_closed": row[11],
                "strategy_name": row[12],
                "symbol": row[13],
                "timeframe": row[14],
                "exchange_name": row[15],
                "display": " ".join(
                    part
                    for part in [
                        row[15],
                        row[12],
                        row[13],
                        row[14],
                    ]
                    if part
                ),
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


def update_user_bots_options(conn, user_exchange_id, update_fields):
    if conn is None:
        return False
    if not update_fields:
        conn.close()
        return False
    cur = conn.cursor()
    try:
        set_clause = sql.SQL(", ").join(
            sql.SQL("{} = %s").format(sql.Identifier(field))
            for field in update_fields
        )
        update = sql.SQL(
            """
            UPDATE user_exchanges
            SET {set_clause}
            WHERE id = %s
            """
        ).format(set_clause=set_clause)
        values = list(update_fields.values())
        values.append(user_exchange_id)

        # 🔍 DEBUG: imprime a query final
        debug_query = cur.mogrify(update, values)
        print("DEBUG SQL:", debug_query.decode("utf-8"))

        cur.execute(update, values)
        conn.commit()
        return cur.rowcount > 0
    except Error as e:
        print(f"update_user_exchange_run_on_server, Database error: {e}")
        traceback.print_exc()
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()
