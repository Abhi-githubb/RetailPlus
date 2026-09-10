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

# Base directory of the repository (always resolved as absolute path)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load local .env file if present
load_dotenv(BASE_DIR / ".env")


def get_database_url() -> str:
    """
    Retrieves and normalizes the database connection URL with strict priority:
    1. Streamlit Cloud Secrets (st.secrets["DATABASE_URL"] or st.secrets["postgres"]["url"])
    2. Environment variable (os.environ["DATABASE_URL"])
    3. Local .env file
    4. SQLite fallback with absolute, writable path
    """
    db_url = None

    # 1. Check Streamlit Cloud secrets if running within Streamlit
    try:
        import streamlit as st
        # Check if secrets are available and non-empty
        if hasattr(st, "secrets") and len(st.secrets) > 0:
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

    # 2. Check environment variables if not found in Streamlit secrets
    if not db_url:
        db_url = os.getenv("DATABASE_URL")

    # 3. Normalize PostgreSQL dialect if provided
    if db_url:
        db_url = db_url.strip()
        # Fix legacy Heroku / Supabase / Neon postgres:// prefix
        if db_url.startswith("postgres://"):
            db_url = "postgresql+psycopg2://" + db_url[len("postgres://"):]
        elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+"):
            db_url = "postgresql+psycopg2://" + db_url[len("postgresql://"):]
        return db_url

    # 4. Fallback to SQLite with absolute writable path
    data_dir = BASE_DIR / "data"
    try:
        data_dir.mkdir(parents=True, exist_ok=True)
        test_file = data_dir / ".write_test"
        test_file.touch()
        test_file.unlink()
        sqlite_file = (data_dir / "retailpulse.db").resolve()
    except Exception:
        # Fallback to system temp directory if repo directory is read-only
        temp_dir = Path(tempfile.gettempdir()) / "retailpulse_data"
        temp_dir.mkdir(parents=True, exist_ok=True)
        sqlite_file = (temp_dir / "retailpulse.db").resolve()

    # Formulate valid SQLAlchemy SQLite URI
    posix_path = sqlite_file.as_posix()
    if posix_path.startswith("/"):
        # Unix/Linux absolute path needs 4 slashes total: sqlite:////path
        return f"sqlite:///{posix_path}"
    else:
        # Windows drive path: sqlite:///C:/path
        return f"sqlite:///{posix_path}"


# Dynamic Database URL
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

# File Paths (Always absolute based on BASE_DIR)
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
