"""
Test simulating a completely fresh clone (clean environment).
Ensures that when no database file exists and no processed CSVs exist,
initialize_database() generates the dataset, cleans it, creates tables,
loads data, and deploys all 9 analytical views.
"""

import tempfile
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from src.database.initializer import initialize_database, REQUIRED_TABLES, REQUIRED_VIEWS


def test_clean_environment_startup():
    # Create isolated clean temp directory simulating a fresh clone
    with tempfile.TemporaryDirectory() as tmpdir:
        clean_db_file = Path(tmpdir) / "fresh_clone.db"
        clean_url = f"sqlite:///{clean_db_file.as_posix()}"

        # Monkeypatch get_database_url and engine in initializer
        import src.database.connection as conn_mod
        import src.database.initializer as init_mod
        import src.database.loader as loader_mod

        test_engine = create_engine(clean_url, connect_args={"check_same_thread": False})
        orig_engine = conn_mod.engine
        orig_init_engine = init_mod.engine
        orig_loader_engine = loader_mod.engine

        try:
            conn_mod.engine = test_engine
            init_mod.engine = test_engine
            loader_mod.engine = test_engine

            # Run initialization with smaller sample for high speed test
            result = initialize_database(
                force=True,
                num_orders=5000,
                num_customers=1000,
                num_products=100,
            )

            assert result["success"] is True, f"Initialization failed: {result.get('error')}"
            assert result["status"] == "initialized"

            # Verify all 6 tables have data
            for tbl in REQUIRED_TABLES:
                assert tbl in result["tables"]
                assert result["tables"][tbl] > 0

            # Verify all 9 views exist
            assert len(result["views_verified"]) == 9
            for view in REQUIRED_VIEWS:
                assert view in result["views_verified"]

        finally:
            conn_mod.engine = orig_engine
            init_mod.engine = orig_init_engine
            loader_mod.engine = orig_loader_engine
            test_engine.dispose()
