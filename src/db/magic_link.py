from psycopg2 import sql, Error


def create_user_magic_link(conn, genie_users_id, email, secret_code, company_id):
    cur = conn.cursor()
    try:
        # Create user
        insert = sql.SQL(
            "INSERT INTO genie_user_login_magic_link (genie_users_id, email, secret_code, company_id, datetime) VALUES (%s, %s, %s, %s, NOW()) RETURNING id"
        )
        print(f"create_user_magic_link, genie_users_id={genie_users_id}, email={email}, secret_code={secret_code}, company_id={company_id}")
        values = (genie_users_id, email, secret_code, company_id)

        cur.execute(insert, values)

        generated_id = cur.fetchone()[0]

        return generated_id
    except Error as e:
        print(f"create_user_magic_link, Database error: {e}")
        return None

    finally:
        conn.commit()
        cur.close()
        conn.close()


def get_magic_link_by_secret_code(conn, secret_code):
    cur = conn.cursor()

    # Query to get genie_user_invitations based on email and secret_code
    select = sql.SQL(
        """
        SELECT i.id, i.email, i.secret_code, i.datetime, i.genie_users_id, c.name AS company_name, c.id AS company_id
        FROM genie_user_login_magic_link i
        INNER JOIN genie_companies c ON i.company_id = c.id
        WHERE i.secret_code = %s
        """
    )

    values = (secret_code, )

    try:
        cur.execute(select, values)
        invitation = cur.fetchone()

        if invitation:
            invitation_data = {
                "id": invitation[0],
                "email": invitation[1],
                "secret_code": invitation[2],
                "datetime": invitation[3],
                "genie_users_id": invitation[4],
                "company_name": invitation[5],
                "company_id": invitation[6],
                # This will provide the company name for the invitation, you can remove this if not needed.
            }
            return invitation_data
        else:
            return None

    except Error as e:
        print(f"get_magic_link_by_secret_code, Database error: {e}")
        return None
    finally:
        cur.close()
        conn.close()


def get_magic_link_by_email(conn, email):
    cur = conn.cursor()

    # Query to get genie_user_invitations based on email and secret_code
    select = sql.SQL(
        """
        SELECT i.id, i.email, i.secret_code, i.datetime, i.genie_users_id, c.name AS company_name 
        FROM genie_user_login_magic_link i
        INNER JOIN genie_companies c ON i.company_id = c.id
        WHERE i.email = %s 
        """
    )

    values = (email,)

    try:
        cur.execute(select, values)
        invitation = cur.fetchone()

        if invitation:
            invitation_data = {
                "id": invitation[0],
                "email": invitation[1],
                "secret_code": invitation[2],
                "datetime": invitation[3],
                "genie_users_id": invitation[4],
                "company_name": invitation[5],
                # This will provide the company name for the invitation, you can remove this if not needed.
            }
            return invitation_data
        else:
            return None

    except Error as e:
        print(f"get_magic_link_by_email, Database error: {e}")
        return None
    finally:
        cur.close()
        conn.close()


def delete_magic_link_by_id(conn, magic_link_id):
    cur = conn.cursor()

    # Query to delete genie_user_login_magic_link based on id
    delete = sql.SQL(
        """
        DELETE FROM genie_user_login_magic_link
        WHERE id = %s
        """
    )

    values = (magic_link_id,)

    try:
        cur.execute(delete, values)
        rows_deleted = cur.rowcount
        if rows_deleted == 0:
            print(f"No magic_link rows deleted, ID {magic_link_id} might not exist.")
            return False
        else:
            print(f"Successfully deleted magic_link with ID {magic_link_id}")
            return True
    except Error as e:
        print(f"delete_magic_link_by_id, Database error: {e}")
        return False
    finally:
        conn.commit()  # Commit the transaction
        cur.close()
        conn.close()
