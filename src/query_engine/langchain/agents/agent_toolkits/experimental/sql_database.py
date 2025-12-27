"""SQL wrapper around SQLDatabase in langchain."""
import logging
from typing import Any, List
from urllib.parse import unquote

import sqlparse
# from langchain.sql_database import SQLDatabase as LangchainSQLDatabase
from src.query_engine.langchain.utilities.sql_database import SQLDatabase as LangchainSQLDatabase

from pydantic.class_validators import validator
from pydantic.config import Extra
from pydantic.env_settings import BaseSettings
from pydantic.main import BaseModel
from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.engine import Engine
from sshtunnel import SSHTunnelForwarder

logger = logging.getLogger(__name__)


# Define a custom exception class
class SQLInjectionError(Exception):
    pass


class InvalidDBConnectionError(Exception):
    pass


class DBConnections:
    db_connections = {}

    @staticmethod
    def add(uri, engine):
        DBConnections.db_connections[uri] = engine


class SSHSettings(BaseSettings):
    db_name: str | None
    host: str | None
    username: str | None
    password: str | None
    remote_host: str | None
    remote_db_name: str | None
    remote_db_password: str | None
    private_key_password: str | None
    db_driver: str | None

    class Config:
        extra = Extra.ignore

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


class FileStorage(BaseModel):
    name: str
    access_key_id: str
    secret_access_key: str
    region: str | None
    bucket: str

    class Config:
        extra = Extra.ignore

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


class DatabaseConnection(BaseModel):
    id: str | None
    alias: str
    use_ssh: bool = False
    uri: str | None
    path_to_credentials_file: str | None
    llm_api_key: str | None = None
    ssh_settings: SSHSettings | None = None
    file_storage: FileStorage | None = None

    @validator("uri", pre=True, always=True)
    def set_uri_without_ssh(cls, v, values):
        if values["use_ssh"] and v:
            raise ValueError("When use_ssh is True don't set uri")
        if not values["use_ssh"] and not v:
            raise ValueError("When use_ssh is False set uri")
        return v


class SQLDatabase(LangchainSQLDatabase):
    """SQL Database.

    Wrapper around SQLDatabase object from langchain. Offers
    some helper utilities for insertion and querying.
    See `langchain documentation <https://tinyurl.com/4we5ku8j>`_ for more details:

    Args:
        *args: Arguments to pass to langchain SQLDatabase.
        **kwargs: Keyword arguments to pass to langchain SQLDatabase.

    """

    @property
    def engine(self) -> Engine:
        """Return SQL Alchemy engine."""
        return self._engine

    @property
    def metadata_obj(self) -> MetaData:
        """Return SQL Alchemy metadata."""
        return self._metadata

    @classmethod
    def from_uri(
            cls, database_uri: str, engine_args: dict | None = None, **kwargs: Any
    ) -> "SQLDatabase":
        """Construct a SQLAlchemy engine from URI."""
        _engine_args = engine_args or {}
        if database_uri.lower().startswith("duckdb"):
            config = {"autoload_known_extensions": False}
            _engine_args["connect_args"] = {"config": config}
        engine = create_engine(database_uri, **_engine_args)
        return cls(engine, **kwargs)

    @classmethod
    def get_sql_engine(
            cls, database_info: DatabaseConnection, refresh_connection=False
    ) -> "SQLDatabase":
        logger.info(f"Connecting db: {database_info.id}")
        if (
                database_info.id
                and database_info.id in DBConnections.db_connections
                and not refresh_connection
        ):
            return DBConnections.db_connections[database_info.id]

        db_uri = unquote(database_info.uri)
        try:
            engine = cls.from_uri(db_uri)
            DBConnections.add(database_info.id, engine)
        except Exception as e:
            raise InvalidDBConnectionError(  # noqa: B904
                f"Unable to connect to db: {database_info.alias}, {e}"
            )
        return engine

    @classmethod
    def from_uri_ssh(cls, database_info: DatabaseConnection):
        file_path = database_info.path_to_credentials_file

        ssh = database_info.ssh_settings
        server = SSHTunnelForwarder(
            (ssh.host, 22),
            ssh_username=ssh.username,
            ssh_password=ssh.password,
            ssh_pkey=file_path,
            ssh_private_key_password=ssh.private_key_password,
            remote_bind_address=(ssh.remote_host, 5432),
        )
        server.start()
        local_port = str(server.local_bind_port)
        local_host = str(server.local_bind_host)

        return cls.from_uri(
            f"{ssh.db_driver}://{ssh.remote_db_name}:{ssh.remote_db_password}@{local_host}:{local_port}/{ssh.db_name}"
        )

    @classmethod
    def parser_to_filter_commands(cls, command: str) -> str:
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
        parsed_command = sqlparse.parse(command)

        for stmt in parsed_command:
            for token in stmt.tokens:
                if (
                        isinstance(token, sqlparse.sql.Token)
                        and token.normalized in sensitive_keywords
                ):
                    raise SQLInjectionError(
                        f"Sensitive SQL keyword '{token.normalized}' detected in the query."
                    )

        return command

    def run_sql(self, command: str, top_k: int = None) -> tuple[str, dict]:
        """Execute a SQL statement and return a string representing the results.

        If the statement returns rows, a string of the results is returned.
        If the statement returns no rows, an empty string is returned.
        """
        with self._engine.connect() as connection:
            command = self.parser_to_filter_commands(command)
            cursor = connection.execute(text(command))
            if cursor.returns_rows and top_k:
                result = cursor.fetchmany(top_k)
                return str(result), {"result": result}
            if cursor.returns_rows:
                result = cursor.fetchall()
                return str(result), {"result": result}
        return "", {}

    # from llama-index's sql-wrapper
    def get_table_columns(self, table_name: str) -> List[Any]:
        """Get table columns."""
        return self._inspector.get_columns(table_name)

    # from llama-index's sql-wrapper
    def get_single_table_info(self, table_name: str) -> str:
        """Get table info for a single table."""
        # same logic as table_info, but with specific table names
        template = (
            "Table '{table_name}' has columns: {columns} "
            "and foreign keys: {foreign_keys}."
        )
        columns = []
        for column in self._inspector.get_columns(table_name):
            columns.append(f"{column['name']} ({str(column['type'])})")
        column_str = ", ".join(columns)
        foreign_keys = []
        for foreign_key in self._inspector.get_foreign_keys(table_name):
            foreign_keys.append(
                f"{foreign_key['constrained_columns']} -> "
                f"{foreign_key['referred_table']}.{foreign_key['referred_columns']}"
            )
        foreign_key_str = ", ".join(foreign_keys)
        return template.format(
            table_name=table_name, columns=column_str, foreign_keys=foreign_key_str
        )
