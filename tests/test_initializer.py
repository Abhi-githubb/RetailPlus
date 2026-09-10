"""
Unit and integration tests for RetailPulse Warehouse Initializer.
Validates automatic schema creation, table population, view verification,
and idempotency.
"""

from src.database.initializer import initialize_database, inspect_warehouse_state, REQUIRED_TABLES, REQUIRED_VIEWS


def test_initialize_database_succeeds_and_verifies_all_entities():
    result = initialize_database()
    assert result["success"] is True
    assert result["status"] in ["ready", "initialized"]
    assert "tables" in result

    # Verify all 6 required tables have records
    for tbl in REQUIRED_TABLES:
        assert tbl in result["tables"], f"Missing table {tbl}"
        assert result["tables"][tbl] > 0, f"Table {tbl} has 0 rows"

    # Verify all 9 required views
    assert len(result["views_verified"]) == 9
    for v in REQUIRED_VIEWS:
        assert v in result["views_verified"], f"Missing view {v}"


def test_warehouse_inspect_state():
    table_counts, failed_views = inspect_warehouse_state()
    assert len(failed_views) == 0, f"Views failed to query: {failed_views}"
    assert table_counts["orders"] > 50000
    assert table_counts["customers"] > 10000


def test_initialize_database_is_idempotent():
    # Calling initialize_database a second time should recognize existing warehouse
    result1 = initialize_database()
    assert result1["success"] is True

    result2 = initialize_database()
    assert result2["success"] is True
    assert result2["status"] == "ready"
    assert result1["tables"]["orders"] == result2["tables"]["orders"]
