"""
Configuration management for RetailPulse.
Loads configuration from Streamlit secrets, environment variables, and .env file.
Prioritizes production PostgreSQL when configured, with robust SQLite fallback.
"""

import os
import sys
import tempfile
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
GENERATED_DATA_DIR = DATA_DIR / "generated"
SQL_DIR = BASE_DIR / "sql"

for d in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, GENERATED_DATA_DIR]:
    try:
        d.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

load_dotenv(BASE_DIR / ".env")


def get_database_url() -> str:
    """Resolve the database URL from Streamlit secrets, environment, or SQLite fallback."""
    db_url = None

    try:
        import streamlit as st
        try:
            if "DATABASE_URL" in st.secrets:
                db_url = str(st.secrets["DATABASE_URL"]).strip()
            elif "database_url" in st.secrets:
                db_url = str(st.secrets["database_url"]).strip()
            elif "postgres" in st.secrets:
                pg = st.secrets["postgres"]
                if isinstance(pg, str):
                    db_url = pg.strip()
                elif isinstance(pg, dict):
                    if "url" in pg:
                        db_url = str(pg["url"]).strip()
                    elif all(k in pg for k in ["host", "user", "password"]):
                        host = pg["host"]
                        user = pg["user"]
                        pw = pg["password"]
                        port = pg.get("port", 5432)
                        dbname = pg.get("database", "postgres")
                        db_url = f"postgresql+psycopg2://{user}:{pw}@{host}:{port}/{dbname}"
        except Exception:
            pass
    except Exception:
        pass

    if not db_url:
        db_url = os.getenv("DATABASE_URL")

    if db_url:
        db_url = db_url.strip()
        if db_url.startswith("postgres://"):
            db_url = "postgresql+psycopg2://" + db_url[len("postgres://"):]
        elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+"):
            db_url = "postgresql+psycopg2://" + db_url[len("postgresql://"):]
        return db_url

    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        test_file = DATA_DIR / ".write_test"
        test_file.touch()
        test_file.unlink()
        sqlite_file = (DATA_DIR / "retailpulse.db").resolve()
    except Exception:
        temp_dir = Path(tempfile.gettempdir()) / "retailpulse_data"
        temp_dir.mkdir(parents=True, exist_ok=True)
        sqlite_file = (temp_dir / "retailpulse.db").resolve()

    return f"sqlite:///{sqlite_file.as_posix()}"


# Resolve once per Python process so every database consumer uses the same URL.
DATABASE_URL = get_database_url()

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_URL = os.getenv("API_URL", f"http://localhost:{API_PORT}")

# Streamlit Configuration
STREAMLIT_PORT = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))
STREAMLIT_ADDRESS = os.getenv("STREAMLIT_SERVER_ADDRESS", "0.0.0.0")

# App Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Bump this when deployment configuration changes; useful for confirming a fresh Cloud process.
CONFIG_VERSION = "2026-09-10-stable-db"

__all__ = [
    "BASE_DIR",
    "DATA_DIR",
    "RAW_DATA_DIR",
    "PROCESSED_DATA_DIR",
    "GENERATED_DATA_DIR",
    "SQL_DIR",
    "get_database_url",
    "DATABASE_URL",
    "API_HOST",
    "API_PORT",
    "API_URL",
    "STREAMLIT_PORT",
    "STREAMLIT_ADDRESS",
    "ENVIRONMENT",
    "LOG_LEVEL",
    "CONFIG_VERSION",
]
