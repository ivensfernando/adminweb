from datetime import datetime
import jwt
from jwt import PyJWTError

from ninja.security import HttpBearer
from ninja.errors import HttpError

from config.settings.base import JWT_SECRET_KEY, JWT_ALGORITHM
# from src.login import create_jwt_token


class AuthBearer(HttpBearer):

    def authenticate(self, request, token: str):
        print(f"AuthBearer, authenticate, request.path={request.path}, token={token}")

        # url_path = request.path
        # if url_path == "/api_auth/pay" or url_path == "/api_auth/config" or url_path == "/api_auth/pay/create-payment-intent" or url_path == "/api_auth/pay/webhook":
        #     user = {"id": 1, "username": "test", "password": "test"}
        #     return create_jwt_token(user)

        try:
            # Decode the token
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])

            # Check if token is expired
            exp = payload.get('exp')
            if exp and datetime.utcnow().timestamp() > exp:
                raise jwt.ExpiredSignatureError()

            # If all checks pass, return the payload (or any value you need)

            # TODO: validate user on DB and check if has permission to access endpoint
            return payload
        except jwt.ExpiredSignatureError:
            print(f"AuthBearer, authenticate, ExpiredSignatureError, request.path={request.path}, token={token}")
            raise HttpError(status_code=401, message="Token expired")
        except jwt.InvalidTokenError:
            print(f"AuthBearer, authenticate, InvalidTokenError, request.path={request.path}, token={token}")
            raise HttpError(status_code=403, message="Invalid token")
        except PyJWTError:
            print(f"AuthBearer, authenticate, PyJWTError, request.path={request.path}, token={token}")
            raise HttpError(status_code=401, message="Invalid token")
        except Exception as e:
            print(f"AuthBearer, authenticate, Exception, request.path={request.path}, token={token}")
            raise HttpError(status_code=500, message=str(e))


auth_api_key_api = AuthBearer()
