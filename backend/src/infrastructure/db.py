"""Azure SQL Database connection/session management (T009).

SQLAlchemy 2.0 with the `mssql+pyodbc` dialect (research.md: no native async MSSQL driver
exists, so database calls run through this synchronous engine from a thread pool via
`starlette.concurrency.run_in_threadpool` at the API layer rather than a native async DBAPI).
SQLite is used automatically for local development/tests when `database_url` is left at
its default, so contributors can run the full test suite without Docker/Azure SQL.
"""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from src.infrastructure.config import get_settings


class Base(DeclarativeBase):
    """Shared declarative base for all domain SQLAlchemy models."""


def _make_engine() -> Engine:
    settings = get_settings()
    connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
    return create_engine(settings.database_url, pool_pre_ping=True, future=True, connect_args=connect_args)


engine: Engine = _make_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db_session() -> Iterator[Session]:
    """FastAPI dependency yielding a request-scoped SQLAlchemy session."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def create_all_tables() -> None:
    """Create tables from metadata. Used by tests and local dev; production uses Alembic migrations."""
    Base.metadata.create_all(bind=engine)
