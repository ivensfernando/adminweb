import traceback

import sqlalchemy
from sqlalchemy import MetaData, Table, inspect
from llama_index.core import SQLDatabase
from sqlalchemy.sql import func
from sqlalchemy.schema import CreateTable

from src.db.login_helpers import getConn
from src.db.table_info_helpers import create_genie_users_db_connection_details, \
    create_genie_users_db_connection_details_column_description_column_distinct, \
    get_genie_users_db_connection_details_by_company_id_join_column_description


def get_all_tables_and_views(
        database: SQLDatabase,
        table_name=None,
        db_schema=None,
        company_id=None,
        resourcename=None,
        genie_users_id=None,
        force_refresh=False,
        db_warehouse=None,
        max_examples_count=1
):
    print(f"get_all_tables_and_views, table_name={table_name}, db_schema={db_schema}, force_refresh={force_refresh}")
    # Check if details for the given company_id are already present

    if not force_refresh:
        existing_details = get_genie_users_db_connection_details_by_company_id_join_column_description(
            conn=getConn(), company_id=company_id, db_schema=db_schema,
            resourcename=resourcename, db_warehouse=db_warehouse,
        )

        filtered_existing_details = [
            t for t in existing_details if t.get("table_schema") and t.get("table_name")
        ]
        for f in existing_details:
            table_schema = f.get("table_schema")
            table_name = f.get("table_name")
            #print(f"existing_details, table_name={table_name}, table_schema={table_schema}, f={f}")



        print(
            f"get_all_tables_and_views, existing_details={len(existing_details)}, filtered_existing_details={len(filtered_existing_details)}")

        if len(filtered_existing_details) > 0:
            return filtered_existing_details
        else:
            print(f"get_all_tables_and_views, filtered_existing_details, failed to fetch data!!!")


    inspector = inspect(database.engine)
    meta = MetaData(bind=database.engine, schema=(None if db_schema == '' else db_schema))
    MetaData.reflect(meta, views=True, schema=(None if db_schema == '' else db_schema))
    if table_name:
        tables = [table_name]
    else:
        print(f"get_all_tables_and_views, tables_from_inspect")
        tables_from_inspect = inspector.get_table_names(schema=(None if db_schema == '' else db_schema)) + inspector.get_view_names(schema=(None if db_schema == '' else db_schema))
        tables = [
            table for table in tables_from_inspect if table and table.lower() in tables_from_inspect
        ]
    list_tables = []
    for table in tables:
        print(f"get_all_tables_and_views, get_columns, table={table}")
        columns = inspector.get_columns(table_name=table, schema=(None if db_schema == '' else db_schema))
        columns = [column for column in columns if column["name"].find(".") < 0]
        columns_ret = []
        for column in columns:
            col_name = column.get("name")
            col_type = column.get("type")
            columns_ret.append(
                {
                    "name": col_name,
                    "type": str(col_type),
                    "description": "",  # TODO add description
                    "categories": ""  # TODO add categories
                }
            )

        foreign_keys = get_all_foreign_keys_for_table(database, table, db_schema)
        examples = get_table_samples(database, table, max_examples_count, db_schema)
        table_schema = get_table_schema(database, table, db_schema)
        description = ""
        if not table_schema:
            print(f"get_all_tables_and_views, SKIP, table_schema is invalid, table={table}")
        else:
            table_info = {
                "table_name": table,
                "table_columns": columns_ret,
                "foreign_keys": foreign_keys,
                "examples": examples,
                "table_schema": table_schema,
                "description": "",
            }
            print(f"get_all_tables_and_views, adding table_info={table}")
            list_tables.append(table_info)

        # Save this data to the database
        create_genie_users_db_connection_details(
            conn=getConn(), table_name=table, table_columns=columns_ret, foreign_keys=foreign_keys, examples=examples,
            company_id=company_id, genie_users_id=genie_users_id, status="COMPLETED", db_schema=db_schema,
            resourcename=resourcename, table_schema=table_schema, description=description, db_warehouse=db_warehouse
        )

    return list_tables


def get_all_foreign_keys_for_table(database: SQLDatabase, table_name, db_schema=None):
    print(f"get_all_foreign_keys_for_table, get_columns, table_name={table_name}, db_schema={db_schema}")
    inspector = inspect(database.engine)
    meta = MetaData(bind=database.engine, schema=(None if db_schema == '' else db_schema))
    MetaData.reflect(meta, views=True, schema=(None if db_schema == '' else db_schema))
    foreign_keys = inspector.get_foreign_keys(table_name=table_name, schema=(None if db_schema == '' else db_schema))
    return foreign_keys


def get_table_samples(database: SQLDatabase, table_name, max_examples_count, db_schema=None):
    print(f"get_table_samples, table_name={table_name}, db_schema={db_schema}, ")
    meta = MetaData(schema=(None if db_schema == '' else db_schema))
    MetaData.reflect(meta, bind=database.engine, views=True, schema=(None if db_schema == '' else db_schema))
    table = Table(table_name, meta, autoload=True, autoload_with=database.engine)

    is_table_found = table_name in meta.tables
    is_found_retry = False

    if not is_table_found:
        # print(f"get_table_samples, try again")
        new_table_name = f"{db_schema}.{table_name}"
        is_found_retry = new_table_name in meta.tables
        # print(f"get_table_samples, try again, is_found_retry={is_found_retry}, new_table_name={new_table_name}")
        if is_found_retry:
            table_name = new_table_name

    # print(f"get_table_samples, meta.tables_len={len(meta.tables)}, is_table_found={is_table_found}, is_found_retry={is_found_retry}, meta.tables.keys={meta.tables.keys()}")
    # Print all table names available in metadata
    for table_name in meta.tables.keys():
        print(f"get_table_samples, table_name={table_name}")

    if is_table_found or is_found_retry:
        try:
            examples_query = (
                sqlalchemy.select(table)
                .with_only_columns(
                    [
                        column
                        for column in meta.tables[table_name].columns
                        if column.name.find(".") < 0
                    ]
                )
                .limit(max_examples_count)
            )
            examples = database.engine.execute(examples_query).fetchall()
            # print(f"get_table_samples, examples_query={examples_query}, examples={examples}")

            examples_dict = []
            columns = [column["name"] for column in examples_query.column_descriptions]
            for example in examples:
                temp_dict = {}
                for index, value in enumerate(columns):
                    temp_dict[value] = str(example[index])
                examples_dict.append(temp_dict)

            # print(f"get_table_samples, examples_dict={examples_dict}")
            return examples_dict
        except Exception as e:
            traceback.print_exc()
            return []

    else:
        return []

def get_table_column_distinct(database: SQLDatabase, table_name, column_dict, db_schema=None):
    meta = MetaData(bind=database.engine, schema=(None if db_schema == '' else db_schema))
    MetaData.reflect(meta, views=True, schema=(None if db_schema == '' else db_schema))
    column_name = column_dict["name"]
    column_type = str(column_dict["type"])


    table = Table(table_name, meta, autoload=True, autoload_with=database.engine, schema=(None if db_schema == '' else db_schema))
    # warehouse bug ?
    field_size_query = sqlalchemy.select(
        [table.c[column_name]]
    ).limit(1)
    print(f"get_table_column_distinct, checking field sizes, field_size_query={field_size_query}")

    field_to_check = database.engine.engine.execute(field_size_query).first()
    if not field_to_check:
        field_to_check = [""]
    field_size = len(str(str(field_to_check[0])))
    if field_size > 50:
        print(f"get_table_column_distinct field_size>50, return. field_size={field_size}, field_to_check={field_to_check}")
        return {
            "column_name": column_name,
            "column_type": column_type,
            "categories": [],
        }

    try:
        cardinality_query = sqlalchemy.select(
            [func.distinct(table.c[column_name])]
        ).limit(200)
        print(f"get_table_column_distinct, checking field cardinality, cardinality_query={cardinality_query}")

        cardinality = database.engine.engine.execute(cardinality_query).fetchall()
    except Exception as e:
        traceback.print_exc()
        print(f"get_table_column_distinct, ERROR, cardinality, {e}")
        return {
            "column_name": column_name,
            "column_type": column_type,
            "categories": [],
        }

    print(f"get_table_column_distinct, checking len cardinality {len(cardinality)}")

    if len(cardinality) > 60:
        return {
            "column_name": column_name,
            "column_type": column_type,
            "categories": [],
        }

    print("get_table_column_distinct, get categories, count, group_by, build query")

    query = sqlalchemy.select(
        [
            table.c[column_name],
            sqlalchemy.func.count(table.c[column_name]),
        ]
    ).group_by(table.c[column_name])

    print(f"get_table_column_distinct, get categories, count, group_by, query={query}")

    categories = database.engine.engine.execute(query).fetchall()
    if 1 < len(categories) <= 60:
        categories = [str(category[0]) for category in categories]
        return {
            "column_name": column_name,
            "column_type": column_type,
            "categories": categories,
        }
    else:
        return None


def get_table_schema(database: SQLDatabase, table_name, db_schema=None):
    meta = MetaData(bind=database.engine, schema=(None if db_schema == '' else db_schema))
    MetaData.reflect(meta, views=True, schema=(None if db_schema == '' else db_schema))

    table = Table(table_name, meta, autoload=True, autoload_with=database.engine, schema=(None if db_schema == '' else db_schema))

    create_table = str(
        CreateTable(table).compile(
            database.engine
        )
    )
    table_schema = f"{create_table.rstrip()}"
    # print(f"Create table schema: table_name={table_name}, db_schema={db_schema}, table_schema={table_schema}")
    return table_schema


def get_all_columns_distinct_for_table(database: SQLDatabase, table_name, db_schema=None):
    inspector = inspect(database.engine)
    table_columns = []
    columns = inspector.get_columns(table_name=table_name, schema=(None if db_schema == '' else db_schema))
    columns = [column for column in columns if column["name"].find(".") < 0]

    for column in columns:
        print(f"Scanning column: {column['name']}")
        table_columns.append(
            get_table_column_distinct(database, table_name, column)
        )


def get_all_db_schemas(database: SQLDatabase):
    inspector = inspect(database.engine)
    return inspector.get_schema_names()

def get_all_db_schemas_by_engine(engine):
    inspector = inspect(engine)
    return inspector.get_schema_names()


def get_table_column_distinct_and_save(
        database: SQLDatabase,
        table_name=None,
        db_schema=None,
        company_id=None,
        resourcename=None,
        db_warehouse=None,
        column_name=None,
):
    column = {
        "name": column_name,
        "type": ""
    }
    table_column_distinct = get_table_column_distinct(
        database=database,
        table_name=table_name,
        column_dict=column,
        db_schema=db_schema
    )
    if not table_column_distinct:
        return None

    processed_categories = table_column_distinct.get("categories", [])

    # Save this data to the database
    create_genie_users_db_connection_details_column_description_column_distinct(
        conn=getConn(),
        table_name=table_name,
        db_schema=db_schema,
        db_warehouse=db_warehouse,
        resourcename=resourcename,
        company_id=company_id,
        column_name=column_name,
        column_distinct=processed_categories,
    )
