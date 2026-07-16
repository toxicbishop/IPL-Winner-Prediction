"""
Utility for database connectivity (SQLite and PostgreSQL).
Provides a unified interface for executing queries and managing connections.
"""

import pandas as pd
from sqlalchemy import create_engine, text

from config import DB_ENGINE, POSTGRES_CONFIG


def get_engine(db_path: str = None):
    """Returns a SQLAlchemy engine."""
    if DB_ENGINE == "postgres":
        url = f"postgresql://{POSTGRES_CONFIG['user']}:{POSTGRES_CONFIG['pass']}@{POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}/{POSTGRES_CONFIG['db']}"
        return create_engine(url)
    else:
        if db_path is None:
            from config import SQLITE_DB_PATH

            db_path = SQLITE_DB_PATH
        return create_engine(f"sqlite:///{db_path}")


def get_connection(db_path: str = None):
    """Returns a connection from the engine."""
    engine = get_engine(db_path)
    return engine.connect()


def execute_query(query: str, params: tuple = None, db_path: str = None):
    """Executes a query and returns the result."""
    engine = get_engine(db_path)
    with engine.begin() as conn:
        if params:
            return conn.execute(text(query), params)
        else:
            return conn.execute(text(query))


def read_query(query: str, params: tuple = None, db_path: str = None) -> pd.DataFrame:
    """Executes a SELECT query and returns a pandas DataFrame."""
    engine = get_engine(db_path)
    # SQLAlchemy connection handles numeric types much better
    return pd.read_sql_query(text(query), engine, params=params)


def get_insert_sql(
    table: str, columns: list, conflict_target: str = None, ignore: bool = False
) -> str:
    """
    Returns the appropriate INSERT SQL for the active DB engine.
    Handles 'INSERT OR REPLACE/IGNORE' for SQLite and 'ON CONFLICT' for PostgreSQL.
    """
    placeholders = ", ".join([f":{c}" for c in columns])
    cols_str = ", ".join(columns)

    if DB_ENGINE == "sqlite":
        action = "REPLACE" if not ignore else "IGNORE"
        return f"INSERT OR {action} INTO {table} ({cols_str}) VALUES ({placeholders})"
    else:
        # PostgreSQL syntax
        if ignore:
            return (
                f"INSERT INTO {table} ({cols_str}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
            )
        if conflict_target:
            updates = ", ".join([f"{c} = EXCLUDED.{c}" for c in columns if c != conflict_target])
            return f"INSERT INTO {table} ({cols_str}) VALUES ({placeholders}) ON CONFLICT ({conflict_target}) DO UPDATE SET {updates}"
        return f"INSERT INTO {table} ({cols_str}) VALUES ({placeholders})"


def execute_upsert(
    conn,
    table: str,
    columns: list,
    values: tuple,
    conflict_target: str = None,
    ignore: bool = False,
):
    sql = get_insert_sql(table, columns, conflict_target, ignore)
    params = dict(zip(columns, values, strict=False))
    conn.execute(text(sql), params)
