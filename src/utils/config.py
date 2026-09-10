"""
Configuration management for RetailPulse.
Loads configuration from environment variables and .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the repository
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load .env file
load_dotenv(BASE_DIR / ".env")

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'data' / 'retailpulse.db'}")

# Normalize sqlite path if relative
if DATABASE_URL.startswith("sqlite:///") and not DATABASE_URL.startswith("sqlite:////") and ":/" not in DATABASE_URL[10:]:
    rel_path = DATABASE_URL.replace("sqlite:///", "")
    abs_path = (BASE_DIR / rel_path).resolve()
    DATABASE_URL = f"sqlite:///{abs_path.as_posix()}"

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

# Paths
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
GENERATED_DATA_DIR = DATA_DIR / "generated"
SQL_DIR = BASE_DIR / "sql"

for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, GENERATED_DATA_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
