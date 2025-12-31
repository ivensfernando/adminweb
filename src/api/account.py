from typing import Optional

from django.http import JsonResponse
from ninja import Router
from pydantic.main import BaseModel

from src.db.company import get_company_by_id, get_users_by_company_id, get_invitation_by_email, delete_invitation_by_id, \
    create_user_invitation
from src.db.history import get_chat_history_count_by_genie_users_id, get_chat_history_count_by_company_id
from src.db.bot_db import get_bot_conn
from src.db.bot_helpers import get_bot_users_by_email, get_user_exchanges_by_user_ids
from src.db.login_helpers import get_user_key_genie, getConn, generate_access_code, create_user, get_user_by_email, \
    update_user_role, delete_user, get_user_by_id
from src.db.stripe_helpers import get_genie_users_payments_by_genie_users_id
from src.db.utils import RECOMMEND_QUESTIONS, CustomJSONEncoder
from src.email.mailgun import send_invite_via_mailgun

account_router = Router(tags=['Account'])


@account_router.get("/account_user_usage")
def account_user_usage(request):
    token_data = request.auth
    print(f"account_user_usage, token_data={token_data}")

    user_id = token_data["user_id"]
    company_id = token_data["company_id"]
    print(f"account_user_usage, user_id={user_id}")
    usage_count = get_chat_history_count_by_company_id(
        conn=getConn(),
        company_id=company_id
    )

    genie_users_payments_and_plan = get_genie_users_payments_by_genie_users_id(
        conn=getConn(),
        genie_users_id=user_id
    )
    print(
        f"account_user_usage, usage_count={usage_count}, genie_users_payments_and_plan={genie_users_payments_and_plan}")

    if not genie_users_payments_and_plan or len(genie_users_payments_and_plan) == 0:
        print(
            f"account_user_usage, QuotaExceeded(), usage_count={usage_count}, genie_users_payments_and_plan={genie_users_payments_and_plan}")
        return JsonResponse(
            {'error': {'message': "Payment Required: Please purchase more credits to continue using the API."}},
            status=402)

    usage_limit = genie_users_payments_and_plan["amount"]
    subscription_start_date = genie_users_payments_and_plan["subscription_start_date"]
    subscription_status = genie_users_payments_and_plan["subscription_status"]
    subscription_current_period_start_date = genie_users_payments_and_plan["subscription_current_period_start_date"]
    subscription_current_period_end_date = genie_users_payments_and_plan["subscription_current_period_end_date"]

    plan = genie_users_payments_and_plan["plan"]

    return JsonResponse({
        "usage_limit": usage_limit,
        "usage_count": usage_count,
        "plan": plan,
        "subscription_start_date": subscription_start_date,
        "subscription_status": subscription_status,
        "subscription_current_period_start_date": subscription_current_period_start_date,
        "subscription_current_period_end_date": subscription_current_period_end_date,
    }, status=200)


@account_router.get("/account_api_key")
def get_account_api_key(request):
    token_data = request.auth
    print(f"get_account_api_key, token_data={token_data}")

    user_id = token_data["user_id"]
    print(f"get_account_api_key, user_id={user_id}")
    user = get_user_key_genie(getConn(), user_id)
    if user is not None:
        return JsonResponse(user, status=200)
    else:
        return JsonResponse({}, status=404)


@account_router.get("/account_company_info")
def get_account_company_info(request):
    token_data = request.auth
    print(f"get_account_company_info, token_data={token_data}")

    user_id = token_data["user_id"]
    company_id = token_data["company_id"]
    print(f"get_account_company_info, user_id={user_id}, company_id={company_id}")
    company = get_company_by_id(conn=getConn(), id=company_id)
    if company is not None:
        print(f"get_account_company_info, user_id={user_id}, company_id={company_id}")
        return JsonResponse(company, status=200)
    else:
        return JsonResponse({}, status=404)


@account_router.get("/users_by_company",
                    response={
                        200: RECOMMEND_QUESTIONS,
                    },
                    )
def get_users_by_company_id_func(request):
    token_data = request.auth
    print(f"get_users_by_company_id_func, token_data={token_data}")

    user_id = token_data["user_id"]
    company_id = token_data["company_id"]
    print(f"get_users_by_company_id_func, user_id={user_id}, company_id={company_id}")
    users = get_users_by_company_id(conn=getConn(), company_id=company_id)
    if users is not None:
        return JsonResponse(
            {
                "result": users
            },
            encoder=CustomJSONEncoder
        )
    else:
        return JsonResponse({"error": "nothing found"}, status=404)


@account_router.get("/get_user_exchages_options")
def get_user_exchages_options(request):
    token_data = request.auth
    print(f"get_user_exchages_options, token_data={token_data}")

    user_id = token_data["user_id"]
    user = get_user_by_id(conn=getConn(), id=user_id)
    if user is None:
        return JsonResponse({"error": "user not found"}, status=404)

    user_name = user["username"]
    bot_users = get_bot_users_by_email(conn=get_bot_conn(), email=user_name)
    if not bot_users:
        return JsonResponse([], safe=False, status=200)
    user_ids = [bot_user["id"] for bot_user in bot_users]
    user_exchanges = get_user_exchanges_by_user_ids(conn=get_bot_conn(), user_ids=user_ids)
    return JsonResponse(user_exchanges, safe=False, status=200)


class InviteWorkspaceSchema(BaseModel):
    email: Optional[str]


@account_router.post(
    "/invite_to_workspace",
    by_alias=True,
    summary="Invite user to join your company",
    description="Invite user to join your company"
)
def invite_to_workspace(request, payload: InviteWorkspaceSchema):
    token_data = request.auth
    print(f"invite_to_workspace, token_data={token_data}")

    user_id = token_data["user_id"]
    company_id = token_data["company_id"]
    username = token_data["username"]
    email = payload.email

    print(f"invite_to_workspace, user_id={user_id}, payload={payload}")
    secret_code = generate_access_code(32)

    invitation = get_invitation_by_email(conn=getConn(), email=email)
    if invitation is not None:
        invitation_id = invitation["id"]
        delete_invitation_by_id(conn=getConn(), invitation_id=invitation_id)

    genie_users_id = create_user(conn=getConn(), username=email, password=secret_code, company_id=company_id,
                                 role="user")
    if not genie_users_id:
        print(f"invite_to_workspace, user already exists, cant be invited")
        genie_users = get_user_by_email(conn=getConn(), email=email)
        if not genie_users:
            print(
                f"invite_to_workspace, failed to create or get user by email ?!?!, user cant be invited, current user username={username}, was inviting email={email}")
            return JsonResponse({}, status=403)
        genie_users_id = genie_users["id"]

    company = get_company_by_id(getConn(), company_id)
    if company is None:
        return JsonResponse({}, status=404)

    # create pending invitation somewhere
    invitation_id = create_user_invitation(conn=getConn(), genie_users_id=genie_users_id, email=email,
                                           secret_code=secret_code,
                                           company_id=company_id, invite_type="invite_workspace", team_id_slack=None,
                                           user_id_slack=None)
    if invitation_id is None:
        print(
            f"invite_to_workspace, Failed to create_user_invitation")
        return JsonResponse({}, status=403)
    # email invite
    response = send_invite_via_mailgun(recipient=email, company_name=company["website"], secret_code=secret_code,
                                       username=username, invite_type="invite_workspace")
    # Validate here
    if response.status_code == 200:
        print("invite_to_workspace, Email sent successfully!")
    else:
        print(
            f"invite_to_workspace, Failed to send the email. Status code: {response.status_code}. Response text: {response.text}")
        return JsonResponse({}, status=429)


class UpdateUserRoleSchema(BaseModel):
    email: str
    role: str


@account_router.post(
    "/update_user_role",
    by_alias=True,
    summary="Update user role",
    description="Update user role"
)
def update_user_role_func(request, payload: UpdateUserRoleSchema):
    token_data = request.auth
    print(f"update_user_role_func, token_data={token_data}")

    user_id = token_data["user_id"]
    company_id = token_data["company_id"]
    username = token_data["username"]

    # cant update yourself
    if username == payload.email:
        print(f"update_user_role_func, failed to update user, you cannot update your own user!")
        return JsonResponse({'error': {'message': "you cannot update your own user"}}, status=403)

    # check if user is on our company
    target_user = get_user_by_email(conn=getConn(), email=payload.email)
    if target_user is None or target_user["company_id"] != company_id:
        print(f"update_user_role_func, failed to update user.")
        return JsonResponse({'error': {'message': "user not valid or not on your company"}}, status=403)

    # check that this user is admin and its allowed to do it
    admin_user = get_user_by_email(conn=getConn(), email=username)
    if admin_user is None or admin_user["role"] != "admin":
        print(f"update_user_role_func, failed to update user, you are not admin!")
        return JsonResponse({'error': {'message': "your user is not valid or you are not admin"}}, status=403)

    print(f"update_user_role_func, user_id={user_id}, payload={payload}")
    update_user_role(conn=getConn(), username=payload.email, role=payload.role)


class DeleteUserSchema(BaseModel):
    email: str


@account_router.post(
    "/delete_user",
    by_alias=True,
    summary="Delete user",
    description="Admins can delete a user from your company by email"
)
def delete_user_func(request, payload: DeleteUserSchema):
    token_data = request.auth
    print(f"delete_user_func, token_data={token_data}")

    user_id = token_data["user_id"]
    company_id = token_data["company_id"]
    username = token_data["username"]

    # cant update yourself
    if username == payload.email:
        print(f"delete_user_func, failed to delete user, you cannot delete your own user!")
        return JsonResponse({'error': {'message': "you cannot delete your own user"}}, status=403)

    # check if user is on our company
    target_user = get_user_by_email(conn=getConn(), email=payload.email)
    if target_user is None or target_user["company_id"] != company_id:
        print(f"delete_user_func, failed to delete user.")
        return JsonResponse({'error': {'message': "user not valid or not on your company"}}, status=403)

    # check that this user is admin and its allowed to do it
    admin_user = get_user_by_email(conn=getConn(), email=username)
    if admin_user is None or admin_user["role"] != "admin":
        print(f"delete_user_func, failed to delete user, you are not admin!")
        return JsonResponse({'error': {'message': "your user is not valid or you are not admin"}}, status=403)

    print(f"delete_user_func, user_id={user_id}, payload={payload}")
    deleted = delete_user(conn=getConn(), username=payload.email)
    if not deleted:
        print(f"delete_user_func, failed to delete user!")
        return JsonResponse({'error': {'message': "failed to delete user"}}, status=403)


class LinkAppUserToCompanySchema(BaseModel):
    email: str
    team_id_slack: str
    user_id_slack: str
    app_type: str


@account_router.post(
    "/link_app_user_to_company",
    by_alias=True,
    summary="Link an App user a company",
    description="Invite user to join your company"
)
def link_app_user_to_company(request, payload: LinkAppUserToCompanySchema):
    token_data = request.auth
    print(f"link_app_user_to_company, token_data={token_data}")

    user_id = token_data["user_id"]
    company_id = token_data["company_id"]
    email = payload.email

    print(f"link_app_user_to_company, user_id={user_id}, payload={payload}")
    secret_code = generate_access_code(32)

    invitation = get_invitation_by_email(conn=getConn(), email=email)
    if invitation is not None:
        invitation_id = invitation["id"]
        delete_invitation_by_id(conn=getConn(), invitation_id=invitation_id)

    genie_users = get_user_by_email(conn=getConn(), email=email)
    if not genie_users:
        print(
            f"link_app_user_to_company, failed to create or get user by email ?!?!, user cant be invited, current user username={email}, was inviting email={email}")
        return JsonResponse({'error': {'message': "invalid_user_email"}}, status=403)
    genie_users_id = genie_users["id"]

    company = get_company_by_id(getConn(), company_id)
    if company is None:
        return JsonResponse({'error': {'message': "invalid_user_company_id"}}, status=403)

    # create pending invitation somewhere
    invitation_id = create_user_invitation(conn=getConn(), genie_users_id=genie_users_id, email=email,
                                           secret_code=secret_code,
                                           company_id=company_id, invite_type="link_app_user_to_company",
                                           team_id_slack=payload.team_id_slack,
                                           user_id_slack=payload.user_id_slack)

    if invitation_id is None:
        print(
            f"invite_to_workspace, Failed to create_user_invitation")
        return JsonResponse({}, status=403)

    # email invite
    response = send_invite_via_mailgun(recipient=email, company_name=company["website"], secret_code=secret_code,
                                       username=email, invite_type="link_app_user_to_company")
    # Validate here
    if response.status_code == 200:
        print("link_app_user_to_company, Email sent successfully!")
    else:
        print(
            f"link_app_user_to_company, Failed to send the email. Status code: {response.status_code}. Response text: {response.text}")
        return JsonResponse({}, status=429)
