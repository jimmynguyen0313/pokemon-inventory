from datetime import date

import pytest

from backend import database
from backend.demo_data import month_start, price_series
from backend.tests.conftest import add_item


# ── Products ─────────────────────────────────────────────────────────────

def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_catalog_is_seeded_on_startup(client):
    products = client.get("/products").json()
    assert len(products) == 15
    assert {"id", "name", "market_value", "set_name"} <= products[0].keys()


@pytest.mark.parametrize("query,expected", [("jungle", 1), ("booster box", 10), ("BUNDLE", 2), ("nothing-matches", 0)])
def test_search_is_case_insensitive_substring(client, query, expected):
    assert len(client.get("/products/search", params={"name": query}).json()) == expected


def test_search_filters_by_product_type(client):
    results = client.get("/products/search", params={"product_type": "Elite Trainer"}).json()
    assert results and all(r["product_type"] == "Elite Trainer Box" for r in results)


def test_product_history_has_todays_price(client):
    history = client.get("/products/jungle-set-booster-box/history").json()
    assert history[-1] == {"date": date.today().isoformat(), "market_value": 2800.0}


# ── Items ────────────────────────────────────────────────────────────────

def test_add_list_and_delete_item(client):
    item_id = add_item(client, quantity=2, price=80.0)
    items = client.get("/items").json()
    assert len(items) == 1
    item = items[0]
    assert item["id"] == item_id
    assert item["cost_basis"] == 160.0
    assert item["market_total"] == 190.0  # 2 × $95 market value
    assert item["gain"] == 30.0
    assert item["gain_pct"] == 18.75

    assert client.delete(f"/items/{item_id}").json()["status"] == "deleted"
    assert client.get("/items").json() == []


def test_purchase_date_defaults_to_today(client):
    add_item(client)
    assert client.get("/items").json()[0]["purchase_date"] == date.today().isoformat()


@pytest.mark.parametrize("body,status", [
    ({"product_id": "does-not-exist", "quantity": 1, "purchase_price": 10}, 404),
    ({"product_id": "scarlet-violet-booster-box", "quantity": 1, "purchase_price": 10, "category_id": 999}, 404),
    ({"product_id": "scarlet-violet-booster-box", "quantity": 0, "purchase_price": 10}, 422),
    ({"product_id": "scarlet-violet-booster-box", "quantity": 1, "purchase_price": -5}, 422),
])
def test_add_item_validation(client, body, status):
    assert client.post("/items", json=body).status_code == status


def test_delete_missing_item_returns_404(client):
    assert client.delete("/items/12345").status_code == 404


def test_items_with_category(client):
    category_id = client.post("/categories", json={"name": "Vault"}).json()["category_id"]
    add_item(client, category_id=category_id)
    assert client.get("/items").json()[0]["category_name"] == "Vault"


# ── Categories ───────────────────────────────────────────────────────────

def test_categories_create_list_and_reject_duplicates(client):
    assert client.post("/categories", json={"name": "Keep", "description": "x"}).status_code == 200
    assert client.post("/categories", json={"name": "Keep"}).status_code == 400
    assert [c["name"] for c in client.get("/categories").json()] == ["Keep"]


# ── Analytics ────────────────────────────────────────────────────────────

def test_summary_for_empty_collection(client):
    s = client.get("/analytics/summary").json()
    assert s["market_value"] == 0
    assert s["unrealized_gain_pct"] is None
    assert s["holdings"] == 0 and s["by_type"] == []


def test_summary_totals_gain_and_allocation(client):
    add_item(client, "scarlet-violet-booster-box", quantity=2, price=80.0)    # worth 190, cost 160
    add_item(client, "crown-zenith-elite-trainer-box", quantity=1, price=50.0)  # worth 35, cost 50
    s = client.get("/analytics/summary").json()
    assert s["market_value"] == 225.0
    assert s["cost_basis"] == 210.0
    assert s["unrealized_gain"] == 15.0
    assert s["unrealized_gain_pct"] == pytest.approx(7.14, abs=0.01)
    assert (s["holdings"], s["units"]) == (2, 3)
    assert s["by_type"][0] == {"label": "Booster Box", "value": 190.0, "share": 84.4}
    assert s["top_gainers"][0]["gain_pct"] == 18.75
    assert s["top_losers"][0]["gain"] == -15.0


def test_allocation_groups_small_slices_into_other(client):
    for product in client.get("/products").json()[:9]:
        add_item(client, product["id"], price=10.0)
    by_set = client.get("/analytics/summary").json()["by_set"]
    assert len(by_set) == 7 and by_set[-1]["label"] == "Other"
    assert sum(s["value"] for s in by_set) == pytest.approx(client.get("/analytics/summary").json()["market_value"])


def test_history_uses_price_on_each_date(client):
    conn = database.get_db()
    conn.execute("INSERT INTO price_history VALUES ('scarlet-violet-booster-box', ?, 50.0)",
                 (month_start(date.today(), 2).isoformat(),))
    conn.commit()
    conn.close()
    add_item(client, quantity=2, price=60.0, purchase_date=month_start(date.today(), 3).isoformat())

    history = client.get("/analytics/history", params={"months": 4}).json()
    assert [p["market_value"] for p in history] == [120.0, 100.0, 100.0, 190.0]  # paid → $50 record → today $95
    assert all(p["cost_basis"] == 120.0 for p in history)


def test_history_excludes_items_before_purchase(client):
    add_item(client, quantity=1, price=60.0)  # bought today
    history = client.get("/analytics/history", params={"months": 3}).json()
    assert [p["market_value"] for p in history] == [0, 0, 95.0]


def test_history_validates_range(client):
    assert client.get("/analytics/history", params={"months": 1}).status_code == 422
    assert client.get("/analytics/history").json() == []


# ── Demo data ────────────────────────────────────────────────────────────

def test_demo_collection_is_seeded(demo_client):
    s = demo_client.get("/analytics/summary").json()
    assert s["holdings"] == 11 and s["units"] == 28
    history = demo_client.get("/analytics/history", params={"months": 24}).json()
    assert len(history) == 24
    assert history[-1]["market_value"] == s["market_value"]


def test_price_series_is_deterministic_and_ends_at_current_price():
    today = date(2026, 11, 5)
    a = price_series("x", 100.0, "2020-01-01", today)
    assert a == price_series("x", 100.0, "2020-01-01", today)
    assert a[today] == 100.0
    assert len(a) == 25
    assert min(price_series("y", 100.0, "2026-06-15", today)) >= date(2026, 6, 15)
