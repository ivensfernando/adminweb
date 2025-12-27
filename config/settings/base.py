"""
Base settings to build other settings files upon.
"""
from pathlib import Path

import logging
import environ
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration


ROOT_DIR = Path(__file__).resolve(strict=True).parent.parent.parent
# data_integration_service/
APPS_DIR = ROOT_DIR / "biidinwebapi"
env = environ.Env()

DATABASE_URL = env.str("DATABASE_URL")
DATABASES = {
    "default": env.db("DATABASE_URL"),
}

DEBUG = env.bool("DJANGO_DEBUG", False)
SECRET_KEY = env("DJANGO_SECRET_KEY", default="test#123#321#test")
API_KEYS = env.list("API_KEYS", default=["123456wer12wegfqwtg24t2462f"])
# OPEN_API_TOKEN = env("OPEN_API_TOKEN", "test123")

DEMO_DATABASE_URL = env.str("DEMO_DATABASE_URL", "")

PINECONE_API_KEY = env.str("PINECONE_API_KEY", "")
PINECONE_ENVIRONMENT = env.str("PINECONE_ENVIRONMENT", "")
PINECONE_EMBEDDING_MODEL = env.str("PINECONE_EMBEDDING_MODEL", "text-embedding-ada-002")


AGENT_LLM_MODEL_DEMO = env.str("AGENT_LLM_MODEL_DEMO", "gpt-3.5-turbo-1106")
AGENT_LLM_MODEL = env.str("AGENT_LLM_MODEL", "gpt-3.5-turbo")
AGENT_LLM_MODEL_CHART = env.str("AGENT_LLM_MODEL_CHART", "gpt-3.5-turbo")
AGENT_LLM_MODEL_EVAL = env.str("AGENT_LLM_MODEL_EVAL", "gpt-3.5-turbo")
AGENT_LLM_ENGINE = env.str("AGENT_LLM_ENGINE", "langchain_agent")

TEMPERATURE = env.float("TEMPERATURE", 0.0)
LANGCHAIN_VERBOSE = env.bool("LANGCHAIN_VERBOSE", False)

LANGCHAIN_MAX_EXECUTION_TIME = env.int("LANGCHAIN_MAX_EXECUTION_TIME", 180)
LANGCHAIN_MAX_ITERATIONS = env.int("LANGCHAIN_MAX_ITERATIONS", 99)

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["*"])
API_KEYS_SECRET_KEY = env.str("API_KEYS_SECRET_KEY", None)
API_KEYS_SECRET_HASHER = env.str("API_KEYS_SECRET_HASHER", "pbkdf2_sha256")


JWT_SECRET_KEY = env.str("JWT_SECRET_KEY", "HZZbTvfASURXaizQFAuxUNHhIOHhWOnB")
JWT_ALGORITHM = env.str("JWT_ALGORITHM", 'HS256')
JWT_EXP_DELTA = env.int("JWT_EXP_DELTA", 365)  # Token expires after


CACHED_HISTORY_ENABLED = env.bool("CACHED_HISTORY_ENABLED", False)


STRIPE_SECRET_KEY = env.str('STRIPE_SECRET_KEY', "")
STRIPE_WEBHOOK_SECRET = env.str('STRIPE_WEBHOOK_SECRET', "")
STRIPE_PUBLISHABLE_KEY = env.str('STRIPE_PUBLISHABLE_KEY', "")
STRIPE_TRIAL_PERIOD_DAYS = env.int("STRIPE_TRIAL_PERIOD_DAYS", 7)


AWS_ACCESS_KEY_ID = env.str("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = env.str("AWS_SECRET_ACCESS_KEY", "")
AWS_STORAGE_BUCKET_NAME = env.str("AWS_STORAGE_BUCKET_NAME", "")
AWS_S3_REGION_NAME = env.str("AWS_S3_REGION_NAME", "nl-ams")
AWS_S3_ENDPOINT_URL = env.str("AWS_S3_ENDPOINT_URL", "")
AWS_S3_FILE_OVERWRITE = env.bool("AWS_S3_FILE_OVERWRITE", False)


# This is the path where Django will collect all static files for deployment
STATIC_ROOT = str(ROOT_DIR / "genieapp/staticfiles")
STATIC_URL = '/genieapp/static/'
STATICFILES_DIRS = [str(APPS_DIR / "genieapp/static")]
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

DJANGO_APPS = [
    'corsheaders',
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    # "django_extensions",
    # "django.contrib.postgres",
    # "psqlextra"
]

LOCAL_APPS = [
    "jobs"
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'src.api.middleware.CacheControlMiddleware'
]

TEMPLATES = [
    {
        # https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(APPS_DIR / "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            "context_processors": [
                "django.template.context_processors.request",
                "django.template.context_processors.static",
            ],
        },
    }
]

CORS_ALLOW_ALL_ORIGINS = True

# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
SENTRY_ENVIRONMENT = env("SENTRY_ENVIRONMENT", default="localhost")

# if SENTRY_ENVIRONMENT != "localhost":
#     LOGGING = {
#         "version": 1,
#         "disable_existing_loggers": True,
#         "formatters": {
#             "verbose": {
#                 "format": "%(levelname)s %(asctime)s %(module)s "
#                           "%(process)d %(thread)d %(message)s"
#             }
#         },
#         "handlers": {
#             "console": {
#                 "level": "DEBUG",
#                 "class": "logging.StreamHandler",
#                 "formatter": "verbose",
#             }
#         },
#         "root": {"level": "INFO", "handlers": ["console"]},
#         "loggers": {
#             "django.db.backends": {
#                 "level": "ERROR",
#                 "handlers": ["console"],
#                 "propagate": False,
#             },
#             # Errors logged by the SDK itself
#             "sentry_sdk": {"level": "ERROR", "handlers": ["console"], "propagate": True},
#             "django.security.DisallowedHost": {
#                 "level": "ERROR",
#                 "handlers": ["console"],
#                 "propagate": False,
#             },
#         },
#     }
    #
    # # Sentry
    # # ------------------------------------------------------------------------------
    # SENTRY_DSN = env("SENTRY_DSN")
    # SENTRY_LOG_LEVEL = env.int("DJANGO_SENTRY_LOG_LEVEL", logging.INFO)
    #
    # sentry_logging = LoggingIntegration(
    #     level=SENTRY_LOG_LEVEL,  # Capture info and above as breadcrumbs
    #     event_level=logging.ERROR,  # Send errors as events
    # )
    # integrations = [
    #     sentry_logging,
    #     DjangoIntegration(),
    # ]
    # sentry_sdk.init(
    #     dsn=SENTRY_DSN,
    #     integrations=integrations,
    #     environment=SENTRY_ENVIRONMENT,
    #     traces_sample_rate=env.float("SENTRY_TRACES_SAMPLE_RATE", default=0.0),
    # )


AUTH_DISABLED = env.bool("AUTH_DISABLED", None)
