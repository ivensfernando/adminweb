import datetime
import re
import traceback
from datetime import date
import hashlib
import json
import os
from decimal import Decimal
from typing import List, Optional, Any

import psycopg2
import sqlglot
from pydantic import BaseModel
import sqlparse

from config.settings.base import AUTH_DISABLED


class DetailUnprocessableEntitySchema(BaseModel):
    loc: List[str]
    msg: str
    type: str


class UnprocessableEntitySchema(BaseModel):
    detail: List[DetailUnprocessableEntitySchema]


class UnauthorizedSchema(BaseModel):
    detail: str


DEFAULT_RESPONSES = {
    401: UnauthorizedSchema,
    422: UnprocessableEntitySchema,
}


class LANGUAGE_TO_SQL(BaseModel):
    sql_query: Optional[str]
    result: Optional[List[Any]]
    error: Optional[Any]


class RECOMMEND_QUESTIONS(BaseModel):
    result: Optional[List[Any]]
    error: Optional[Any]


class COUNT_RESPONSE(BaseModel):
    count: Optional[int]
    error: Optional[Any]


class RUN_SQL(BaseModel):
    result: Optional[List[Any]]
    error: Optional[str]


class DatabaseConnectionSchema(BaseModel):
    name: Optional[str]
    host: Optional[str]
    port: Optional[str]
    ssl: Optional[bool]
    databasename: Optional[str]
    username: Optional[str]
    password: Optional[str]
    apikey: Optional[str]
    resourcename: Optional[str]
    connection_string_url: Optional[str]
    db_type: Optional[str]


def extract_sample_data(data: list) -> str:
    sample_data = []

    for item in data:
        # Temporarily add the item to the sample_data to check its total length when serialized
        sample_data.append(item)
        temp_str = json.dumps(sample_data, separators=(',', ':'), cls=CustomJSONEncoder)

        if len(temp_str) > 2000:
            # If the serialized string is too long, remove the last added item and break
            sample_data.pop()
            break

    # Return the optimized JSON string
    return json.dumps(sample_data, separators=(',', ':'), cls=CustomJSONEncoder)


def validate_postgres_dsn(dsn):
    try:
        parsed = psycopg2.extensions.parse_dsn(dsn)

        # Check for essential components
        if not all(key in parsed for key in ["user", "password", "host", "port", "dbname"]):
            return False

        # Additional validation can be done here if needed

        return True
    except psycopg2.ProgrammingError:
        return False


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime) or isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        return super(CustomJSONEncoder, self).default(obj)


def sanitize_sql_sqlglot(query):
    try:
        sanitized_query = sqlglot.transpile(query)
        return sanitized_query
    except Exception as e:
        traceback.print_exc()
        print(f"Failed to sanitize_sql_sqlglot query={query}: {e}")
        return query


def sanitize_sql_keywords(query) -> str:
    sensitive_keywords = [
        "DROP",
        "DELETE",
        "UPDATE",
        "INSERT",
        "GRANT",
        "REVOKE",
        "ALTER",
        "TRUNCATE",
        "MERGE",
        "EXECUTE",
    ]
    parsed_command = sqlparse.parse(query)

    for stmt in parsed_command:
        for token in stmt.tokens:
            if (
                    isinstance(token, sqlparse.sql.Token)
                    and token.normalized in sensitive_keywords
            ):
                return ""

    return query


def query_planner(query: str, max_cost: float = 50000.0, max_rows: int = 500, conn=None):
    # print(f"query_planner, query={query}")
    cursor = conn.cursor()

    explain_query = f"EXPLAIN (FORMAT JSON) {query}"
    # print(f"query_planner, explain_query={explain_query}")

    cursor.execute(explain_query)
    results = cursor.fetchone()
    result = results[0]
    # print(f"query_planner, results={results}")

    # Parse the JSON output
    # explain_data = json.loads(result[0])
    # print(f"query_planner, explain_data={explain_data}")

    # print(f"query_planner, result[0]={result[0]}")

    # Retrieve the total cost of the query from the JSON output
    total_cost = result[0].get("Plan", {}).get("Total Cost", 0)
    total_rows = result[0].get("Plan", {}).get("Total Rows", 0)

    print(f"query_planner, total_cost={total_cost}, result[0]={result[0]}")

    # Return True if the total cost is below the max_cost threshold, otherwise False
    maxCost = total_cost <= max_cost
    maxRows = total_rows <= max_rows

    return maxCost & maxRows


def create_fake_user(url_path):
    fake_usr = {
        # "id": 1,
        # "user_id": 1,
        "id": 3,
        "user_id": 3,
        "key_hash": 123,
        "usage_limit": 100,
        "usage_count": 1,
        "customer_id": 1,
        "genie_users_id": 1,
        # "company_id": 5,
        "company_id": 1,
        "allowed_paths": url_path
    }
    print(f"create_fake_user, AUTH_DISABLED={AUTH_DISABLED}, fake_usr={fake_usr}, skip auth ...")
    return fake_usr


def generate_api_key() -> str:
    """Generate a secure API key using SHA-256."""
    random_bytes = os.urandom(32)  # Generate 32 random bytes
    api_key = hashlib.sha256(random_bytes).hexdigest()  # Create a SHA-256 hash
    return api_key


def get_dialect_name(db_type: str) -> str:
    mapping = {
        "postgres": "PostgreSQL",
        "mariadb": "MariaDB",
        "mysql": "MySQL",
        "sqlite": "SQLite",
        "mssql": "Microsoft SQL Server",
        "oracle": "Oracle",
        "snowflake": "Snowflake",
        "databricks": "Databricks",
    }
    return mapping.get(db_type.lower(), "Unknown")


def add_driver_to_connection_string(connection_string: str) -> str:
    if not connection_string:
        raise ValueError("Empty connection string provided.")

    # Map starting patterns of connection strings to their respective drivers
    driver_mapping = {
        "postgresql://": "postgresql+psycopg2://",
        "postgres://": "postgresql+psycopg2://",
        "mysql://": "mysql+pymysql://",
        "sqlite://": "sqlite+pysqlite://",
        # Note: SQLite often doesn't require a specific driver, but pysqlite is a common one
        "mssql://": "mssql+pyodbc://",
        "oracle://": "oracle+cx_oracle://",
        "snowflake://": "snowflake://",
        "databricks://": "databricks://",
        "trino://": "trino://"
    }

    for pattern, replacement in driver_mapping.items():
        if connection_string.startswith(pattern):
            return connection_string.replace(pattern, replacement, 1)  # replace only the first occurrence

    raise ValueError(f"Unsupported or unrecognized connection string format: {connection_string}")


def format_history(chat_history):
    """
    Format the history into a condensed format.
    :param chat_history: List of history records returned from get_history_by_user_and_types
    :return: A list of formatted messages.
    """

    formatted_history = []

    for message in chat_history:
        formatted_history.append(f"question={message['question']}:answer={message['answer']}")

    return formatted_history[::-1]  # reverse the list for the desired order


def format_query(db_type, schema, query):
    if db_type == 'postgresql':
        return f"SET search_path TO {schema}; {query}"
    elif db_type == 'oracle':
        return query.replace("TABLE_NAME",
                             f"{schema}.TABLE_NAME")  # This is a simple replace, consider more robust mechanisms
    elif db_type == 'trino':
        return f"USE {schema}"
    elif db_type == 'db2':
        return f"SET SCHEMA = '{schema}'; {query}"
    elif db_type == 'mssql':
        return query.replace("TABLE_NAME", f"[{schema}].[TABLE_NAME]")
    elif db_type == 'mysql':
        return f"USE {schema}; {query}"
    elif db_type == "snowflake":
        return f"ALTER SESSION SET search_path='{schema}'"
    elif db_type == "oracle":
        return f"ALTER SESSION SET CURRENT_SCHEMA='{schema}'"
    elif db_type == 'bigquery':
        return f"SET @@dataset_id='{schema}'"
    else:
        raise ValueError(f"Unsupported db_type: {db_type}")


def use_warehouse(db_type, db_warehouse):
    if db_warehouse and db_type == 'snowflake':
        return f"USE WAREHOUSE {db_warehouse};"
    else:
        return None


def contains_line_breaks(input_string: str) -> bool:
    return "\n" in input_string


def format_sql_query(sql_query: str) -> str:
    comments = [
        match.group() for match in re.finditer(r"--.*$", sql_query, re.MULTILINE)
    ]
    sql_query_without_comments = re.sub(r"--.*$", "", sql_query, flags=re.MULTILINE)

    if contains_line_breaks(sql_query_without_comments.strip()):
        return sql_query

    parsed = sqlparse.format(sql_query_without_comments, reindent=True)

    return parsed + "\n" + "\n".join(comments)


def remove_schema_from_query(sql_query, db_schema):
    # Define the pattern to match the schema followed by a dot.
    # We use \b for word boundary to ensure we match the schema name exactly,
    # and \. to match the dot character (escaped because dot has a special meaning in regex).
    pattern = r'\b' + re.escape(db_schema) + r'\.\b'

    # Use re.sub() to replace the found pattern with an empty string.
    # This effectively removes the schema and the dot from the query.
    modified_query = re.sub(pattern, '', sql_query)

    return modified_query


# formatted_query = format_query('postgresql', 'myschema', 'SELECT * FROM application_opened LIMIT 10')


def extract_keys(json_data):
    if not json_data or not isinstance(json_data, list):
        return ""

    # Using a set to hold unique keys
    unique_keys = set()

    for item in json_data:
        if isinstance(item, dict):
            unique_keys.update(item.keys())

    # Joining the unique keys into a comma-separated string
    return ', '.join(unique_keys)


def get_first_exception(error):
    tb_list = traceback.format_exception(type(error), error, error.__traceback__)
    first_exception = tb_list[0] if len(tb_list) > 1 else "No exception found"
    return first_exception


# Word lists, for the sake of this example we're using simple lists
# but, you can expand them or use some cool/adjective word lists
ADJECTIVES = ["mystic", "silent", "bold", "ancient", "bright", "daring", "brave"]
NOUNS = ["river", "mountain", "forest", "sky", "ocean", "star", "cloud"]


def cool_name_generator(input_string):
    # Create an MD5 hash of the input
    hashed = hashlib.md5(input_string.encode()).hexdigest()

    # Convert some characters of the hash into integers for indexing
    adj_index = int(hashed[:2], 16) % len(ADJECTIVES)  # taking the first 2 characters
    noun_index = int(hashed[2:4], 16) % len(NOUNS)  # taking the next 2 characters

    # Use the indices to pick words from the lists
    name = f"{ADJECTIVES[adj_index]}-{NOUNS[noun_index]}"
    return name


allowed_tables = [
    "ccxt_binance_ohlcv_1h",
    "coinmarketcap_coinmap",
    "coinmarketcap_defycoin",
    "coinmarketcap_defycoinmetadatav2",
    "coinmarketcap_quoteslatest",
    "coinmarketcap_tickerlatest",
    "covalent_chain",
    "covalent_event",
    "covalent_eventaggregations1hour",
    "defytrends_mapcovalentcoinmarketcap",
    "github_repodailycommitactivity",
    "github_repositories",
    "github_repositorycontributorweeklycommitstatistics",
    "github_repositorydependenciesstatistics",
    "github_repositorydependency",
    "github_repositorylanguagesstatistics",
    "github_repositorysearchgroupcount",
    "github_repositorystatistics",
    "google_trends",
    "ingest_fearandgreed",
    "intotheblock_summary",
    "nag",
    "news_newsaggregations1hour",
    "news_newsarticle",
    "nfts_summary",
    "nfts_timeseries",
    "nvt",
    "reddit_metrics",
    "reddit_posts",
    "score_defy",
    "score_market",
    "score_news",
    "score_onchain",
    "score_social",
    "social_metrics",
    "tvl",
    "twitter_influencers",
    "twitter_tweet",
    "twitter_tweet_count_hourly",
    "twitter_tweetsentimentaggregations1hour",
    "whalealert",
    "yahoo_finance_ohlcv_1h",
]

disallowed_tables = [
    "account_emailaddress",
    "account_emailconfirmation",
    "auth_group",
    "auth_group_permissions",
    "auth_permission",
    "django_admin_log",
    "django_celery_beat_clockedschedule",
    "django_celery_beat_crontabschedule",
    "django_celery_beat_intervalschedule",
    "django_celery_beat_periodictask",
    "django_celery_beat_periodictasks",
    "django_celery_beat_solarschedule",
    "django_celery_results_chordcounter",
    "django_celery_results_groupresult",
    "django_celery_results_taskresult",
    "django_content_type",
    "django_migrations",
    "django_session",
    "django_site",
    "users_user",
    "users_user_groups",
    "users_user_user_permissions",
    "api_keys_ingest",
    "api_keys_frontend",
    "genie_users",
    "genie_users_database_connection",
    "genie_users_payments",
    "genie_payment_plan"
]
