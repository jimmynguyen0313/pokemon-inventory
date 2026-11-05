import pytest
from fastapi.testclient import TestClient

from backend import database


@pytest.fixture
def client(tmp_path, monkeypatch):
    """API client on a fresh, empty-collection database (catalog seeded, no demo holdings)."""
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test.db")
    monkeypatch.setenv("DEMO_DATA", "0")
    from backend.app import app

    with TestClient(app) as c:
        yield c


@pytest.fixture
def demo_client(tmp_path, monkeypatch):
    """API client on a fresh database with the demo collection and price history."""
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "demo.db")
    monkeypatch.setenv("DEMO_DATA", "1")
    from backend.app import app

    with TestClient(app) as c:
        yield c


def add_item(client, product_id="scarlet-violet-booster-box", quantity=1, price=80.0, **extra):
    body = {"product_id": product_id, "quantity": quantity, "purchase_price": price, **extra}
    response = client.post("/items", json=body)
    assert response.status_code == 200, response.text
    return response.json()["item_id"]
