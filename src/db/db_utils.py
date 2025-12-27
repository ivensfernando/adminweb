import itertools
import traceback

import typing

from src.db.database_connection import get_database_connection_by_company_id
from src.db.login_helpers import getConn
from src.db.table_info import get_all_tables_and_views
from src.db.utils import sanitize_sql_sqlglot, add_driver_to_connection_string
from sqlalchemy import create_engine

InfoSchemaCache = dict
Schema = dict
Relation = dict


def get_custom_driver_connection(resourcename: str, company_id: int):
    try:

        if resourcename is None:
            print(f"get_custom_driver_connection, cant connect to db, invalid resourcename")
            return None, None
        DATABASE_URL_CUSTOM, db_type = get_connection_string_url(company_id=company_id, resourcename=resourcename)
        if DATABASE_URL_CUSTOM is None:
            print(
                f"get_custom_driver_connection, get_connection_string_url, ERROR: failed to obtain valid connection_string_url!!! ")
            return None, None

        # print(f"get_custom_driver_connection, connecting to db, DATABASE_URL_CUSTOM={DATABASE_URL_CUSTOM}")
        DATABASE_URL_CUSTOM_DRIVER = add_driver_to_connection_string(DATABASE_URL_CUSTOM)
        engine = create_engine(DATABASE_URL_CUSTOM_DRIVER)
        return engine, db_type
    except Exception as e:
        print(f"get_custom_driver_connection, cant connect to db, e={e}")
        traceback.print_exc()
        return None, None


def get_connection_string_url(company_id, resourcename):
    db_connections = get_database_connection_by_company_id(conn=getConn(), company_id=company_id)
    for c in db_connections:
        if c["resourcename"] == resourcename:
            DATABASE_URL_CUSTOM = c["connection_string_url"]

            if c["db_type"] is not None:
                db_type = c["db_type"]
            else:
                db_type_new = get_database_type(DATABASE_URL_CUSTOM)
                if db_type_new is not None:
                    db_type = db_type_new
            return DATABASE_URL_CUSTOM, db_type
    return None, None


def execute_query(engine, sql_query):
    try:
        sanitized_query_sqlglot = sanitize_sql_sqlglot(sql_query)
        with engine.connect() as connection:
            print(f"execute_query, sql_query={sql_query}, sanitized_query_sqlglot={sanitized_query_sqlglot}")
            execution = connection.execute(sql_query)
            result = execution.fetchall()

            columns = execution.keys()
            columns = [item for item in columns]
            formatted_result = [dict(zip(columns, row)) for row in result]
            return formatted_result
    except Exception as e:
        traceback.print_exc()
        print(f"Error, execute_query, Failed, sql_query={sql_query}: error={e}")
        return []


def get_database_type(connection_string_url: str) -> str | None:
    if not connection_string_url:
        return None

    # Map starting patterns of connection strings to their respective database types
    db_type_mapping = {
        "postgresql://": "postgresql",
        "postgres://": "postgresql",
        "mysql://": "mysql",
        "sqlite://": "sqlite",
        "mssql://": "mssql",
        "oracle://": "oracle",
        "snowflake://": "snowflake",
        "databricks://": "databricks",
        "trino://": "trino"
    }

    for pattern, db_type in db_type_mapping.items():
        if connection_string_url.startswith(pattern):
            return db_type

    print(f"get_database_type, Unsupported or unrecognized connection string format")
    return None


def extract_granular(conn, DATABASE_URL, db_type, database, company_id, db_schema=None, resourcename=None,
                     user_id=None):
    if db_type != "mysql" and db_type != "mariadb" and db_type != "postgres":
        list_tables = get_all_tables_and_views(database=database, db_schema=db_schema, company_id=company_id,
                                               resourcename=resourcename, genie_users_id=user_id)
        return list_tables

    db_schema_ret = get_db_schema(conn, DATABASE_URL, db_type, db_schema)
    # print(f"extract_granular, db_schema_ret={db_schema_ret}")
    index = 1
    if len(db_schema_ret['schemata']) == 1:
        index = 0
    schemata = db_schema_ret['schemata'][index]
    tables = schemata['tables']
    list_tables = []
    for table in tables:
        tables_dict = {}
        tables_dict['table_name'] = table['name']
        tables_dict['table_columns'] = []
        for column in table['columns']:
            d = (column['name'], column['data_type'])
            tables_dict['table_columns'].append(d)
        list_tables.append(tables_dict)
    return list_tables


def get_db_schema(conn, DATABASE_URL, db_type, db_schema=None):
    cursor = conn.cursor()
    if db_type == "mysql" or db_type == "mariadb":
        cursor.execute(GET_DB_SCHEMA_MYSQL)
    else:
        cursor.execute(GET_DB_SCHEMA_POSTGRES, (DATABASE_URL,))

    return _parse_schema_cursor(cursor, db_schema)


# def _get_column_index(cursor, column_name):
#     desc = cursor.description
#     print(f"_get_column_index, column_name={column_name}, cursor.description={cursor.description}")
#     return [col[0] for col in desc].index(column_name)

# def _get_column_index(cursor, column_name):
#     for i, column in enumerate(cursor.description):
#         if column.name == column_name:
#             return i
#     return -1

def _get_column_index(cursor, column_name):
    desc = cursor.description
    # print(f"_get_column_index, column_name={column_name}, cursor.description={cursor.description}")
    try:
        # Try accessing name attribute (assuming psycopg2-like behavior)
        return [col.name for col in desc].index(column_name)
    except AttributeError:
        # Fall back to tuple-based access (assuming MariaDB/MySQL-like behavior)
        return [col[0] for col in desc].index(column_name)


def _parse_schema_cursor(cur, db_schema=None):
    """Extract structured schema data from an existing Postgres database.

    cur is a cursor from an open psycopg2 connection to the target database.
    """
    info_schema_dict: InfoSchemaCache = {
        "name": "",
        "description": None,
        "schemata": [],
    }

    db_idx = _get_column_index(cur, "name")
    db_description_idx = _get_column_index(cur, "description")
    table_type_idx = _get_column_index(cur, "schemata.tables.type")
    table_comment_idx = _get_column_index(cur, "schemata.tables.description")
    schema_idx = _get_column_index(cur, "schemata.name")
    schema_comment_idx = _get_column_index(cur, "schemata.description")
    rel_idx = _get_column_index(cur, "schemata.tables.name")

    results = cur.fetchall()
    grouped = itertools.groupby(results, key=lambda row: row[schema_idx])
    group_counts = {key: len(list(group)) for key, group in grouped}

    # print(f"_parse_schema_cursor, results_len={len(results)}, group_counts={len(group_counts)}")

    if len(group_counts) == 1:
        # print(f"_parse_schema_cursor, results_len={len(results)}, group_counts={len(group_counts)}, reset db_schema to None")
        db_schema = None

    for i, (schema_name, schema_rows) in enumerate(
            itertools.groupby(results, key=lambda row: row[schema_idx])
    ):
        # print(f"_parse_schema_cursor, schema_name={schema_name}, db_schema={db_schema}")
        if db_schema is not None and db_schema != schema_name:
            # print(f"_parse_schema_cursor, loop, schema_name={schema_name}")
            continue

        schema: Schema = {
            "name": schema_name,
            "description": None,
            "is_foreign": False,
            "tables": [],
            "views": [],
        }
        for j, (rel_name, rel_rows) in enumerate(
                itertools.groupby(schema_rows, key=lambda row: row[rel_idx])
        ):
            # print(f"_parse_schema_cursor, rel_name={rel_name}, rel_rows={rel_rows}")

            rel: Relation = {"name": rel_name, "description": None, "columns": []}
            table_type: typing.Optional[typing.Literal["tables", "views"]] = None

            for k, row in enumerate(rel_rows):
                table_type = "views" if row[table_type_idx] == "VIEW" else "tables"
                if i == 0:
                    info_schema_dict["description"] = row[db_description_idx]
                    info_schema_dict["name"] = row[db_idx]
                if j == 0:
                    schema["description"] = row[schema_comment_idx]
                if k == 0:
                    rel["description"] = row[table_comment_idx]
                col = {}
                for column, value in zip(cur.description, row):
                    try:
                        column_name = column.name
                    except AttributeError:
                        column_name = column[0]
                    path = column_name.split(".")
                    if "columns" in path:
                        col[path[-1]] = value

                if col["name"] is not None:
                    rel["columns"].append(col)

            if rel["name"] and table_type:
                schema[table_type].append(rel)

        info_schema_dict["schemata"].append(schema)

    return info_schema_dict


# Query includes schemas, tables, columns, and associated comments
GET_DB_SCHEMA_POSTGRES = """
SELECT
    (SELECT pg_catalog.shobj_description(d.oid, 'pg_database')
    FROM   pg_catalog.pg_database d
    WHERE  datname = %s) AS "description",
    "information_schema"."schemata"."catalog_name" as "name",
    "information_schema"."schemata"."schema_name" as "schemata.name",
    "information_schema"."tables"."table_name" as "schemata.tables.name",
    "information_schema"."tables"."table_type" as "schemata.tables.type",
    "information_schema"."columns"."column_name" AS "schemata.tables.columns.name",
    "information_schema"."columns"."ordinal_position" AS "schemata.tables.columns.ordinal_position",
    "information_schema"."columns"."column_default" AS "schemata.tables.columns.column_default",
    "information_schema"."columns"."is_nullable" AS "schemata.tables.columns.is_nullable",
    "information_schema"."columns"."data_type" AS "schemata.tables.columns.data_type",
    "information_schema"."columns"."character_maximum_length" AS "schemata.tables.columns.character_maximum_length",
    obj_description(
        quote_ident("information_schema"."schemata"."schema_name")::regnamespace::oid,
        'pg_namespace'
    ) AS "schemata.description",
    -- NOTE: it is important to use the concat operator || and not the concat function below, as the former returns
    -- NULL if any component is NULL and avoids breaking obj_description with queries for the non-existent relation "."
    obj_description(
        (quote_ident("information_schema"."schemata"."schema_name") || '.' || quote_ident("information_schema"."tables"."table_name"))::regclass::oid,
        'pg_class'
    )  AS "schemata.tables.description",
    col_description(
        (quote_ident("information_schema"."schemata"."schema_name")  || '.' || quote_ident("information_schema"."tables"."table_name"))::regclass::oid,
        "information_schema"."columns"."ordinal_position"
    ) AS "schemata.tables.columns.description"
FROM "information_schema"."schemata"
LEFT JOIN "information_schema"."tables" ON "information_schema"."schemata"."schema_name" = "information_schema"."tables"."table_schema"
LEFT JOIN "information_schema"."columns" ON "information_schema"."tables"."table_name" = "information_schema"."columns"."table_name" AND "information_schema"."tables"."table_schema" = "information_schema"."columns"."table_schema"
WHERE "information_schema"."schemata"."schema_name" != 'pg_catalog'
AND "information_schema"."schemata"."schema_name" != 'information_schema'
AND "information_schema"."schemata"."schema_name" != 'pg_toast'
ORDER BY "schemata.name", "schemata.tables.name";
"""

GET_DB_SCHEMA_MYSQL = """
SELECT
    '' AS "description",  
    DATABASE() AS "name",
    t.TABLE_SCHEMA AS "schemata.name",
    t.TABLE_NAME AS "schemata.tables.name",
    t.TABLE_TYPE AS "schemata.tables.type",
    c.COLUMN_NAME AS "schemata.tables.columns.name",
    c.ORDINAL_POSITION AS "schemata.tables.columns.ordinal_position",
    c.COLUMN_DEFAULT AS "schemata.tables.columns.column_default",
    c.IS_NULLABLE AS "schemata.tables.columns.is_nullable",
    c.DATA_TYPE AS "schemata.tables.columns.data_type",
    c.CHARACTER_MAXIMUM_LENGTH AS "schemata.tables.columns.character_maximum_length",
    '' AS "schemata.description",  
    t.TABLE_COMMENT AS "schemata.tables.description",
    c.COLUMN_COMMENT AS "schemata.tables.columns.description"
FROM information_schema.TABLES t
LEFT JOIN information_schema.COLUMNS c ON t.TABLE_NAME = c.TABLE_NAME AND t.TABLE_SCHEMA = c.TABLE_SCHEMA
WHERE t.TABLE_SCHEMA NOT IN ('information_schema', 'mysql', 'performance_schema', 'sys')
ORDER BY "schemata.name", "schemata.tables.name";
"""
