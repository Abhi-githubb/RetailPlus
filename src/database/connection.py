"""
Database Connection and Session Management for RetailPulse.
Supports PostgreSQL (Production/Cloud) and SQLite (Local Fallback),
with dynamic connection resolution, pooling, and health inspection.
"""

from contextlib import contextmanager
from typing import Generator, Tuple
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from src.utils.logger import logger
from src.utils.config import get_database_url

# SQLAlchemy Base
Base = declarative_base()


def create_configured_engine():
    """Builds and returns an engine configured for the current DATABASE_URL."""
    url = get_database_url()
    is_sqlite = url.startswith("sqlite")

    engine_args = {
        "echo": False,
        "future": True,
    }

    if is_sqlite:
        engine_args["connect_args"] = {"check_same_thread": False}
    else:
        engine_args["pool_size"] = 10
        engine_args["max_overflow"] = 20
        engine_args["pool_pre_ping"] = True

    return create_engine(url, **engine_args)


# Shared engine instance
engine = create_configured_engine()
is_sqlite = engine.dialect.name == "sqlite"

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Context manager for transactional database operations."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database transaction rolled back due to error: {e}")
        raise
    finally:
        session.close()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for database session injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> Tuple[bool, str]:
    """Verifies that the database is reachable and returns status."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        dialect = "SQLite" if engine.dialect.name == "sqlite" else "PostgreSQL"
        return True, f"Connected successfully ({dialect})"
    except Exception as e:
        return False, f"Connection failed: {str(e)}"
