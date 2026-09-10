"""
Integration tests for RetailPulse FastAPI REST endpoints.
"""

from fastapi.testclient import TestClient
from app.api.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database_connected"] is True


def test_api_summary_endpoint():
    response = client.get("/api/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_orders" in data
    assert "total_revenue" in data
    assert data["total_orders"] > 0
    assert data["total_revenue"] > 0


def test_api_sales_trends():
    response = client.get("/api/sales?granularity=monthly")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "total_revenue" in data[0]


def test_api_categories():
    response = client.get("/api/categories")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "category" in data[0]


def test_api_products():
    response = client.get("/api/products?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    assert "product_name" in data[0]


def test_api_regions():
    response = client.get("/api/regions")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 5


def test_api_cohorts():
    response = client.get("/api/cohorts")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "cohort_month" in data[0]
