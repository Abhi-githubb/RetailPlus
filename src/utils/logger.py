"""
Logging utility for RetailPulse.
Provides structured, standardized logging across the ETL pipeline, API, and analytics engine.
"""

import logging
import os
import sys
from datetime import datetime

def setup_logger(name: str = "retailpulse", level: str = None) -> logging.Logger:
    """Configures and returns a logger instance with standardized formatting."""
    log_level = level or os.getenv("LOG_LEVEL", "INFO").upper()
    numeric_level = getattr(logging, log_level, logging.INFO)

    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(numeric_level)

        # Formatter
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Console Handler with safe encoding
        if hasattr(sys.stdout, "reconfigure"):
            try:
                sys.stdout.reconfigure(encoding="utf-8")
            except Exception:
                pass
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File Handler (logs directory)
        log_dir = os.path.join(os.getcwd(), "logs")
        os.makedirs(log_dir, exist_ok=True)
        file_handler = logging.FileHandler(
            os.path.join(log_dir, f"retailpulse_{datetime.now().strftime('%Y%m%d')}.log"),
            encoding="utf-8",
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

logger = setup_logger()
