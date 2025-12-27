import datetime
from typing import Optional, Any
from typing import List
import traceback
import pytz  # This module helps with timezone conversions

from django.contrib.auth.hashers import make_password
from django.http import HttpRequest
# from ninja.compatibility import get_headers
from ninja.security import APIKeyHeader

from config.settings.base import AUTH_DISABLED, API_KEYS_SECRET_KEY, API_KEYS_SECRET_HASHER
from starlette.exceptions import HTTPException as HttpError

from src.auth.jwt_auth import AuthBearer
from src.db.history import get_chat_history_count_by_genie_users_id, get_chat_history_count_by_company_id
from src.db.login_helpers import getConn, login_user_with_key_genie
from src.db.stripe_helpers import get_genie_users_payments_by_genie_users_id, get_stripe_subscription
from src.db.utils import create_fake_user


class QuotaExceeded(HttpError):
    def __init__(self):
        super().__init__(status_code=402,
                         detail="Payment Required: Please purchase more credits to continue using the API.")


class Forbidden(HttpError):
    def __init__(self):
        super().__init__(status_code=403,
                         detail="Forbidden request: The endpoint you are trying to use is not available in your plan. Please purchase another plan to use this the API endpoint.")


class DoesNotExist(HttpError):
    def __init__(self):
        super().__init__(status_code=403,
                         detail="Object does not exist: The key you are trying to use is not valid. Please purchase a plan to use this the API endpoint.")


class APIKey(APIKeyHeader):
    param_name = "X-API-Key"

    def __init__(self, keys: List[str]):
        super().__init__()
        self.keys = keys
        print(f"APIKeys, __init__, keys={keys}")

    def authenticate(self, request, key):
        url_path = request.path
        if key is None:
            if AUTH_DISABLED is not None:
                return create_fake_user(url_path)
            return None
        try:
            print(f"APIKey, authenticate, key={key}, self.keys={self.keys}, url_path={url_path}")
            if key in self.keys:
                return create_fake_user(url_path)

            # api_key_obj = login_user_with_key(getConn(), key)
            key_hash = make_password(password=key, salt=API_KEYS_SECRET_KEY, hasher=API_KEYS_SECRET_HASHER)
            api_key_obj = login_user_with_key_genie(conn=getConn(), key_hash=key_hash)
            print(f"APIKey, authenticate, key_hash={key_hash}, api_key_obj={api_key_obj}")
            if api_key_obj is None:
                raise DoesNotExist()
            allowed_paths = api_key_obj["allowed_paths"]
            if len(allowed_paths) > 0 and url_path not in allowed_paths:
                print(
                    f"APIKey, authenticate, Forbidden, allowed_paths={allowed_paths}, key={key}, self.keys={self.keys}, url_path={url_path}")
                raise Forbidden()

            genie_users_id = api_key_obj["genie_users_id"]
            company_id = api_key_obj["company_id"]
            usage_count = get_chat_history_count_by_company_id(conn=getConn(), company_id=company_id)
            print(f"APIKey, authenticate, usage_count={usage_count}")

            if usage_count is None:
                print(
                    f"APIKey, authenticate, Forbidden, Failed to calculate usage. allowed_paths={allowed_paths}, url_path={url_path}")
                raise QuotaExceeded()

            genie_users_payments_and_plan = get_genie_users_payments_by_genie_users_id(conn=getConn(),
                                                                                       genie_users_id=genie_users_id)
            print(f"APIKey, authenticate, genie_users_payments_and_plan={genie_users_payments_and_plan}")
            if not genie_users_payments_and_plan or len(genie_users_payments_and_plan) == 0:
                print(f"APIKey, authenticate, QuotaExceeded, usage_count={usage_count}, url_path={url_path}")
                raise QuotaExceeded()

            usage_limit = genie_users_payments_and_plan["amount"]
            subscription_id = genie_users_payments_and_plan["subscription_id"]
            subscription_current_period_end_date = genie_users_payments_and_plan["subscription_current_period_end_date"]
            subscription_status = genie_users_payments_and_plan["subscription_status"]

            if not subscription_id:
                print(f"APIKey, authenticate, subscription_id is None, usage_count={usage_count}, url_path={url_path}")
                raise QuotaExceeded()

            if subscription_status != "trialing" and subscription_status != "active":
                print(
                    f"APIKey, authenticate, invalid subscription_status, subscription_status={subscription_status}, usage_count={usage_count}, url_path={url_path}")
                raise QuotaExceeded()

            current_period_end = subscription_current_period_end_date.astimezone(pytz.utc)

            if datetime.datetime.utcnow().replace(tzinfo=pytz.utc) > current_period_end:
                print(
                    f"APIKey, authenticate, current_period_end >  utcnow, current_period_end={current_period_end}, utcnow={datetime.datetime.utcnow().replace(tzinfo=pytz.utc)}, usage_count={usage_count}, url_path={url_path}")
                raise QuotaExceeded()

            if 0 < usage_limit <= usage_count:
                print(
                    f"APIKey, authenticate, QuotaExceeded, usage_count={usage_count}, usage_limit={usage_limit}, url_path={url_path}")
                raise QuotaExceeded()

            # stripe_subscription_data = get_stripe_subscription(subscription_id)
            # print(f"APIKey, authenticate, stripe_subscription_data={stripe_subscription_data}")

            # Attach the usage_limit to the request object
            request.usage_limit = usage_limit

            # Attach the usage_count to the request object
            request.usage_remaining = usage_limit - usage_count

            return api_key_obj
        except Exception as e:
            print(f"APIKey, authenticate, Exception, e={e}")
            traceback.print_exc()
            return None


class CustomAuth:
    def __init__(self, api_keys: list):
        self.api_key_auth = APIKey(api_keys)
        self.jwt_auth = AuthBearer()

    def _get_bearer_token(self, request: HttpRequest) -> Optional[str]:
        auth_value = request.headers.get("Authorization") or request.META.get("HTTP_AUTHORIZATION")
        if not auth_value:
            return None

        parts = auth_value.split(" ")
        if parts[0].lower() != "bearer":
            return None

        return " ".join(parts[1:])

    def _get_api_key(self, request: HttpRequest) -> Optional[str]:
        header_name = self.api_key_auth.param_name  # e.g. "X-API-Key"

        api_key = request.headers.get(header_name)
        if api_key:
            return api_key

        # Fallback: Django exposes headers in META as HTTP_<HEADER_NAME>
        meta_name = "HTTP_" + header_name.upper().replace("-", "_")
        return request.META.get(meta_name)

    def __call__(self, request) -> Optional[Any]:
        # First, try JWT auth
        token = self._get_bearer_token(request)
        if token:
            jwt_user = self.jwt_auth.authenticate(request, token)
            if jwt_user:
                return jwt_user

        url_path = request.path
        if url_path == "/api/healthcheck" \
                or url_path == "/api/models" \
                or url_path == "/api/pay" \
                or url_path == "/api/pay/config" \
                or url_path == "/api/pay/return" \
                or url_path == "/api/pay/webhook":
            return create_fake_user(url_path)

        # If JWT auth fails, try API key auth
        print("CustomAuth, if JWT auth fails, try API key auth")
        api_key = self._get_api_key(request)
        print(f"CustomAuth, api_key={api_key}")

        return self.api_key_auth.authenticate(request, api_key)
