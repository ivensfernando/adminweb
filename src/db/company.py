from psycopg2 import sql, Error


def create_company(conn, name, website):
    cur = conn.cursor()
    try:
        # Create user
        insert = sql.SQL(
            "INSERT INTO genie_companies (name, website, datetime) VALUES (%s, %s, NOW()) RETURNING id"
        )
        print(f"create_company, name={name}, website={website}")
        values = (name, website)

        cur.execute(insert, values)

        generated_id = cur.fetchone()[0]

        return generated_id
    except Error as e:
        print(f"create_company, Database error: {e}")
        return None

    finally:
        conn.commit()
        cur.close()
        conn.close()


def get_company_by_id(conn, id):
    cur = conn.cursor()

    # Check user credentials
    select = sql.SQL(
        "SELECT id, name, website, datetime FROM genie_companies WHERE id = %s"
    )

    values = (id,)

    try:
        cur.execute(select, values)
        plan = cur.fetchone()

        if plan:
            return {
                "id": plan[0],
                "name": plan[1],
                "website": plan[2],
                "datetime": plan[3],
            }
        else:
            return None
    except Error as e:
        print(f"get_company_by_id, Database error: {e}")
        return None
    finally:
        cur.close()
        conn.close()


def get_users_by_company_id(conn, company_id):
    cur = conn.cursor()

    # Query to join genie_users and genie_companies based on company_id
    select = sql.SQL(
        """
        SELECT u.id, u.username, u.datetime, u.database_url, u.stripe_customer_id, u.role, u.team_id_slack, c.name AS company_name 
        FROM genie_users u
        INNER JOIN genie_companies c ON u.company_id = c.id
        WHERE c.id = %s
        """
    )

    values = (company_id,)

    try:
        cur.execute(select, values)
        users = cur.fetchall()

        users_data = []
        for user in users:
            user_entry = {
                "id": user[0],
                "username": user[1],
                "datetime": user[2],
                "stripe_customer_id": user[4],
                "role": user[5],
                "team_id_slack": user[6],
                "company_name": user[7]
                # This will have the company name for each user, you can remove this if not needed.
            }
            users_data.append(user_entry)

        return users_data
    except Error as e:
        print(f"get_users_by_company_by_id, Database error: {e}")
        return None
    finally:
        cur.close()
        conn.close()


def create_user_invitation(conn, genie_users_id, email, secret_code, company_id, invite_type, team_id_slack, user_id_slack):
    cur = conn.cursor()
    try:
        # Create user
        insert = sql.SQL(
            "INSERT INTO genie_user_invitations (genie_users_id, email, secret_code, company_id, invite_type, team_id_slack, user_id_slack, datetime) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW()) RETURNING id"
        )
        print(f"create_user_invitation, genie_users_id={genie_users_id}, email={email}, secret_code={secret_code}, company_id={company_id}")
        values = (genie_users_id, email, secret_code, company_id, invite_type, team_id_slack, user_id_slack)

        cur.execute(insert, values)

        generated_id = cur.fetchone()[0]

        return generated_id
    except Error as e:
        print(f"create_user_invitation, Database error: {e}")
        return None

    finally:
        conn.commit()
        cur.close()
        conn.close()


def get_invitation_by_secret_code(conn, secret_code):
    cur = conn.cursor()

    # Query to get genie_user_invitations based on email and secret_code
    select = sql.SQL(
        """
        SELECT i.id, i.email, i.secret_code, i.datetime, i.genie_users_id, i.team_id_slack, i.user_id_slack, i.invite_type, c.name AS company_name, c.id AS company_id
        FROM genie_user_invitations i
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
                "team_id_slack": invitation[5],
                "user_id_slack": invitation[6],
                "invite_type": invitation[7],
                "company_name": invitation[8],
                "company_id": invitation[9],
                # This will provide the company name for the invitation, you can remove this if not needed.
            }
            return invitation_data
        else:
            return None

    except Error as e:
        print(f"get_invitation_by_email_and_secret_code, Database error: {e}")
        return None
    finally:
        cur.close()
        conn.close()


def get_invitation_by_email(conn, email):
    cur = conn.cursor()

    # Query to get genie_user_invitations based on email and secret_code
    select = sql.SQL(
        """
        SELECT i.id, i.email, i.secret_code, i.datetime, i.genie_users_id, i.team_id_slack, i.user_id_slack, i.invite_type, c.name AS company_name 
        FROM genie_user_invitations i
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
                "team_id_slack": invitation[5],
                "user_id_slack": invitation[6],
                "invite_type": invitation[7],
                "company_name": invitation[8],
                # This will provide the company name for the invitation, you can remove this if not needed.
            }
            return invitation_data
        else:
            return None

    except Error as e:
        print(f"get_invitation_by_email, Database error: {e}")
        return None
    finally:
        cur.close()
        conn.close()


def delete_invitation_by_id(conn, invitation_id):
    cur = conn.cursor()

    # Query to delete genie_user_invitations based on id
    delete = sql.SQL(
        """
        DELETE FROM genie_user_invitations
        WHERE id = %s
        """
    )

    values = (invitation_id,)

    try:
        cur.execute(delete, values)
        rows_deleted = cur.rowcount
        if rows_deleted == 0:
            print(f"No rows deleted, ID {invitation_id} might not exist.")
            return False
        else:
            print(f"Successfully deleted invitation with ID {invitation_id}")
            return True
    except Error as e:
        print(f"delete_invitation_by_id, Database error: {e}")
        return False
    finally:
        conn.commit()  # Commit the transaction
        cur.close()
        conn.close()
