"""Pricing API client tests with the HTTP layer faked out (no network or API key needed)."""

from datetime import date

import pytest
import requests

from backend import database, pokemon_api, sync_products

API_PRODUCT = {
    "id": 501,
    "name": "Pokémon Stellar Crown Booster Box",
    "productType": "Booster Box",
    "prices": {"market": 120.5},
    "setName": "Stellar Crown",
    "imageCdnUrl": "https://example.com/sc.png",
    "releaseDate": "2024-09-13",
}


class FakeResponse:
    def __init__(self, payload, status=200):
        self.payload, self.status = payload, status

    def json(self):
        return self.payload

    def raise_for_status(self):
        if self.status >= 400:
            raise requests.HTTPError(f"{self.status} error")


@pytest.fixture
def fake_api(monkeypatch):
    """Set an API key and route requests.get to canned responses; records the calls made."""
    calls = []
    monkeypatch.setattr(pokemon_api, "API_KEY", "test-key")

    def fake_get(url, params=None, headers=None, timeout=None):
        calls.append({"url": url, "params": params, "headers": headers})
        if url.endswith("/sealed-products/missing"):
            return FakeResponse({}, status=404)
        if url.endswith("/sealed-products/501"):
            return FakeResponse({"data": API_PRODUCT})
        return FakeResponse({"data": [API_PRODUCT]})

    monkeypatch.setattr(pokemon_api.requests, "get", fake_get)
    return calls


def test_fetch_products_maps_fields_and_sends_key(fake_api):
    products = pokemon_api.fetch_products("stellar")
    assert products == [{
        "id": "501", "name": API_PRODUCT["name"], "product_type": "Booster Box", "market_value": 120.5,
        "description": "Stellar Crown", "images_url": "https://example.com/sc.png",
        "set_name": "Stellar Crown", "release_date": "2024-09-13",
    }]
    assert fake_api[0]["params"]["search"] == "stellar"
    assert fake_api[0]["headers"] == {"Authorization": "Bearer test-key"}


def test_get_product_by_id(fake_api):
    assert pokemon_api.get_product_by_id("501")["market_value"] == 120.5
    assert pokemon_api.get_product_by_id("missing") is None


def test_sync_endpoint_upserts_products_and_records_price(client, fake_api):
    assert client.post("/products/sync").json() == {"status": "synced", "count": 1}
    assert any(p["id"] == "501" for p in client.get("/products").json())
    assert client.get("/products/501/history").json() == [{"date": date.today().isoformat(), "market_value": 120.5}]
    assert client.get("/products/501").json()["name"] == API_PRODUCT["name"]


def test_sync_cli(client, fake_api, monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["sync_products", "--limit", "5"])
    sync_products.main()
    assert "Synced 1 products" in capsys.readouterr().out
    assert fake_api[-1]["params"]["limit"] == 5


@pytest.mark.parametrize("call", [
    lambda: pokemon_api.fetch_products(),
    lambda: pokemon_api.get_product_by_id("501"),
    lambda: pokemon_api.sync_products_to_db(database.get_db()),
])
def test_client_degrades_gracefully_without_api_key(client, monkeypatch, call):
    monkeypatch.setattr(pokemon_api, "API_KEY", "")
    assert call() in ([], None, 0)


@pytest.mark.parametrize("call", [
    lambda: pokemon_api.fetch_products(),
    lambda: pokemon_api.sync_products_to_db(database.get_db()),
])
def test_client_handles_network_errors(client, monkeypatch, call):
    monkeypatch.setattr(pokemon_api, "API_KEY", "test-key")

    def boom(*args, **kwargs):
        raise requests.ConnectionError("network down")

    monkeypatch.setattr(pokemon_api.requests, "get", boom)
    assert call() in ([], 0)


def test_missing_product_endpoint(client, monkeypatch):
    monkeypatch.setattr(pokemon_api, "API_KEY", "")
    assert client.get("/products/nope").json() == {"error": "Product not found"}
