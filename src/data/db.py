import duckdb
import pandas as pd
from typing import Optional, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.utils.config import config
from src.utils.logging import get_logger

logger = get_logger("data.db")

# SQLAlchemy Engine & Session Factory
engine = create_engine(config.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_duckdb_connection(read_only: bool = True) -> duckdb.DuckDBPyConnection:
    """Returns a connection to the historical Transfermarkt DuckDB instance."""
    if not config.DUCKDB_PATH.exists():
        raise FileNotFoundError(f"DuckDB database file not found at: {config.DUCKDB_PATH}")
    return duckdb.connect(str(config.DUCKDB_PATH), read_only=read_only)


def query_duckdb(query: str, params: Optional[list] = None) -> pd.DataFrame:
    """Executes a SQL query against DuckDB and returns a pandas DataFrame."""
    conn = get_duckdb_connection(read_only=True)
    try:
        if params:
            df = conn.execute(query, params).df()
        else:
            df = conn.execute(query).df()
        return df
    except Exception as e:
        logger.error(f"DuckDB Query failed: {e}\nQuery: {query}")
        raise e
    finally:
        conn.close()


def get_db_session() -> Session:
    """Yields a database session for application data (SQLAlchemy)."""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # caller manages or uses dependency context
