import os
from typing import Optional

from django.http import JsonResponse
from ninja import Router, Schema
import jwt
from pydantic.main import BaseModel

import stripe

from config.settings.base import JWT_EXP_DELTA, JWT_SECRET_KEY, JWT_ALGORITHM, DEMO_DATABASE_URL
from datetime import datetime, timedelta

from src.db.company import create_company, get_invitation_by_secret_code, delete_invitation_by_id, get_company_by_id
from src.db.database_connection import create_or_update_user_db_connection
# from src.db.db_utils import get_database_type
from src.db.login_helpers import getConn, get_user_by_email, create_user, update_user_stripe_customer_id, login_user, \
    update_user_team_id_and_user_id, update_user_password, generate_access_code, get_user_by_id
from src.db.magic_link import create_user_magic_link, get_magic_link_by_email, delete_magic_link_by_id, \
    get_magic_link_by_secret_code
from src.email.mailgun import send_invite_via_mailgun

login_router = Router(tags=['Login/Logout'])

# For sample support and debugging, not required for production:
stripe.set_app_info(
    'biidinwebapi',
    version='0.0.1',
    url='https://wapi.biidin.com')

stripe.api_version = '2020-08-27'
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')

stripe.api_key = STRIPE_SECRET_KEY


class SignupSchema(Schema):
    company_name: Optional[str]
    company_website: str
    email: str
    password: str


class LoginSchema(Schema):
    email: str
    password: str


@login_router.get('/login')
def get_root(request):
    # You need to return a HttpResponse with the rendered template.
    from django.shortcuts import render
    return render(request, 'login.html')


@login_router.get('/signup')
def get_root(request):
    # You need to return a HttpResponse with the rendered template.
    from django.shortcuts import render
    return render(request, 'signup.html')


@login_router.get('/home')
def get_root(request):
    # You need to return a HttpResponse with the rendered template.
    from django.shortcuts import render
    return render(request, 'home.html')


@login_router.post("/signup")
def signup(request, user: SignupSchema):
    # create company using company_website
    conn = getConn()
    name = user.company_name
    website = user.company_website

    user_exists = get_user_by_email(conn=getConn(), email=user.email)
    if user_exists is not None:
        return JsonResponse({'error': {'message': "user already exists"}}, status=417)

    company_id = create_company(conn=conn, name=name, website=website)
    if company_id is None:
        return JsonResponse({'error': {'message': "company website already in use"}},
                            status=422)

    generated_id = create_user(
        conn=getConn(), username=user.email, password=user.password, company_id=company_id,
        role="admin"
    )
    if generated_id:
        customer = stripe.Customer.create(email=user.email)
        update_user_stripe_customer_id(getConn(), user.email, customer.id)

        connection_string_url = DEMO_DATABASE_URL

        # db_type = get_database_type(connection_string_url)
        create_or_update_user_db_connection(
            conn=getConn(),
            user_id=generated_id,
            name="",
            host="",
            port="",
            ssl="",
            databasename="",
            username="",
            password="",
            apikey="",
            resourcename="",
            connection_string_url="",
            # db_type=db_type,
            company_id=company_id,
        )

        return JsonResponse({}, status=200)
    else:
        return JsonResponse({'error': {'message': "failed to create user"}}, status=417)


@login_router.post("/login")
def login(request, user: LoginSchema):
    user_info = login_user(getConn(), user.email, user.password)
    if user_info is not None:
        if user_info["stripe_customer_id"] is None:
            customer = stripe.Customer.create(email=user.email)
            update_user_stripe_customer_id(getConn(), user.email, customer.id)
            user_info.stripe_customer_id = customer.id

        jwt_token = create_jwt_token(user_info)
        return JsonResponse({'token': jwt_token}, status=200)
    else:
        return JsonResponse({}, status=401)


@login_router.post('/logout')
def get_root(request):
    return JsonResponse({"message": "ok"}, status=200)


@login_router.get('/logout')
def get_root(request):
    # You need to return a HttpResponse with the rendered template.
    from django.shortcuts import render
    return render(request, 'logout.html')


@login_router.get('/account')
def get_root(request):
    # You need to return a HttpResponse with the rendered template.
    from django.shortcuts import render
    return render(request, 'account.html')


def create_jwt_token(user):
    payload = {
        'user_id': user.get("id"),
        'username': user.get("username"),
        'exp': datetime.utcnow() + timedelta(days=JWT_EXP_DELTA),
        "stripe_customer_id": user.get("stripe_customer_id"),
        "company_id": user.get("company_id"),
        "role": user.get("role"),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, JWT_ALGORITHM)


class AcceptInviteWorkspaceSchema(BaseModel):
    secret_code: Optional[str]
    new_password: Optional[str]


@login_router.post(
    "/update_user_with_secret_code",
    by_alias=True,
    summary="Update user password",
    description="Update user password with email and secret_code"
)
def accept_invite_workspace(request, payload: AcceptInviteWorkspaceSchema):
    # validate invite code
    invitation = get_invitation_by_secret_code(conn=getConn(), secret_code=payload.secret_code)
    if invitation is None:
        print(f"accept_invite_workspace, invitation not found, secret_code={payload.secret_code}")
        return JsonResponse({'error': {'message': "invitation_not_found"}}, status=403)

    email = invitation["email"]
    invite_type = invitation["invite_type"]

    if invite_type == "link_app_user_to_company":
        team_id_slack = invitation["team_id_slack"]
        user_id_slack = invitation["user_id_slack"]

        invitation_company_id = invitation["company_id"]
        genie_users = get_user_by_email(conn=getConn(), email=email)
        if not invitation or invitation_company_id != genie_users["company_id"]:
            print(
                f"link_app_user_to_company, failed link user. invitation company is not same as user company. invitation_company_id={invitation_company_id}, invitation={invitation}")
            return JsonResponse({'error': {'message': "invalid_user_company_id"}}, status=403)

        update_user_team_id_and_user_id(conn=getConn(), username=email, team_id_slack=team_id_slack,
                                        user_id_slack=user_id_slack)

    else:
        # update user password
        print(f"accept_invite_workspace, invitation found, update user password, email={email}")
        updated = update_user_password(conn=getConn(), username=email, new_password=payload.new_password)
        if not updated:
            return JsonResponse({'error': {'message': "failed_to_update_password"}}, status=403)

    # delete invite code
    deleted = delete_invitation_by_id(conn=getConn(), invitation_id=invitation["id"])
    if not deleted:
        return JsonResponse({'error': {'message': "failed_to_delete_invitation"}}, status=403)


class SendMagicLinkSchema(BaseModel):
    email: Optional[str]


@login_router.post(
    "/send_magic_link",
    by_alias=True,
    summary="send magic link to login user",
    description="Send magic link to login user without password"
)
def send_magic_link(request, payload: SendMagicLinkSchema):
    email = payload.email

    print(f"send_magic_link, email={email}, payload={payload}")
    secret_code = generate_access_code(32)

    user_from_db = get_user_by_email(conn=getConn(), email=email)
    if user_from_db is None:
        return JsonResponse({'error': {'message': "user does not exist"}}, status=417)

    company_id = user_from_db["company_id"]
    genie_users_id = user_from_db["id"]

    magic_link = get_magic_link_by_email(conn=getConn(), email=email)
    if magic_link is not None:
        magic_link_id = magic_link["id"]
        delete_magic_link_by_id(conn=getConn(), magic_link_id=magic_link_id)

    company = get_company_by_id(getConn(), company_id)
    if company is None:
        return JsonResponse({'error': {'message': "company does not exist"}}, status=417)

    # create magic_link
    magic_link_id = create_user_magic_link(conn=getConn(), genie_users_id=genie_users_id, email=email,
                                           secret_code=secret_code,
                                           company_id=company_id)
    if magic_link_id is None:
        print(
            f"send_magic_link, Failed to create_user_invitation")
        return JsonResponse({'error': {'message': "failed to create magic link"}}, status=417)

    subject = f"Passwordless authentication - Genie AI"

    # email invite
    response = send_invite_via_mailgun(recipient=email, company_name=company["website"], secret_code=secret_code,
                                       username=email, invite_type="send_magic_link",
                                       subject=subject)
    # Validate here
    if response.status_code == 200:
        print("send_magic_link, Email sent successfully!")
    else:
        print(
            f"send_magic_link, Failed to send the email. Status code: {response.status_code}. Response text: {response.text}")
        return JsonResponse({}, status=429)


class LoginUserWithMagicLinkSchema(BaseModel):
    secret_code: Optional[str]


@login_router.post(
    "/login_user_with_magic_link",
    by_alias=True,
    summary="Login user passwordless",
    description="Login user with a magic link provided via email"
)
def login_user_with_magic_link(request, payload: LoginUserWithMagicLinkSchema):
    # validate magic_link
    magic_link = get_magic_link_by_secret_code(conn=getConn(), secret_code=payload.secret_code)
    if magic_link is None:
        print(f"login_user_with_magic_link, magic_link not found, secret_code={payload.secret_code}")
        return JsonResponse({'error': {'message': "magic_link_not_found"}}, status=403)

    genie_users_id = magic_link["genie_users_id"]
    genie_users = get_user_by_id(conn=getConn(), id=genie_users_id)
    if genie_users is None:
        print(f"login_user_with_magic_link, get_user_by_id, user not found genie_users_id={genie_users_id}")
        return JsonResponse({'error': {'message': "failed_to_find_user"}}, status=403)

    # delete invite code
    deleted = delete_magic_link_by_id(conn=getConn(), magic_link_id=magic_link["id"])
    if not deleted:
        return JsonResponse({'error': {'message': "failed_to_delete_magic_link"}}, status=403)

    jwt_token = create_jwt_token(genie_users)
    return JsonResponse({'token': jwt_token}, status=200)
