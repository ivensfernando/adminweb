from ninja import NinjaAPI

from config.settings.base import API_KEYS
# from src.api.database_connection import database_router
# from src.api.editor import editor_router
# from src.api.guardrails import guardrails_router
# from src.api.openapi import openapi_router
# from src.api.openapi_stream import openapi_stream_router
# from src.api.s3 import s3_router

from src.api.stripe import stripe_router

from src.api.account import account_router

from src.api.login import login_router
# from src.api.table_info import table_info_router
from src.auth.custom_auth import CustomAuth

custom_auth = CustomAuth(API_KEYS)
api = NinjaAPI(
    auth=custom_auth,
    version="v0.1.3",
)

# api.add_router("", openapi_router)
# api.add_router("", openapi_stream_router)
api.add_router("", stripe_router)
api.add_router("", account_router)
# api.add_router("", editor_router)
# api.add_router("", table_info_router)
# api.add_router("", guardrails_router)
# api.add_router("", database_router)
# api.add_router("", s3_router)

api_auth = NinjaAPI(
    version="v0.1.2",
)
api_auth.add_router("", login_router)


@api.get(
    "/healthcheck",
    auth=None,
)
def healthcheck(request):
    return 200, {"message": "ok"}
