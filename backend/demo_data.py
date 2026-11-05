"""Demo data: price history and a sample collection.

The live demo starts from an empty database on every deploy, so a fresh
database gets two years of monthly price history for every product and a
sample collection to explore. Prices are illustrative, not market data.
Set DEMO_DATA=0 to start with an empty collection instead.
"""

import math
import os
import random
import zlib
from datetime import date

from backend.database import get_db

HISTORY_MONTHS = 24

# Monthly drift and volatility by product age: vintage boxes trend up
# slowly and steadily, recent sets swing more.
VINTAGE = (0.010, 0.035)
MODERN = (0.018, 0.070)

CATEGORIES = [
    ("Long-term hold", "Sealed product kept as an investment"),
    ("To open", "Planned for opening or playing"),
    ("For sale", "Listed or ready to sell"),
]

# (product_id, quantity, months_ago_purchased, category index)
COLLECTION = [
    ("jungle-set-booster-box", 1, 22, 0),
    ("evolving-skies-booster-box", 2, 20, 0),
    ("brilliant-stars-booster-box", 2, 17, 0),
    ("charizard-ultra-premium-collection", 1, 15, 0),
    ("crown-zenith-elite-trainer-box", 4, 14, 2),
    ("sv151-booster-bundle", 6, 12, 1),
    ("obsidian-flames-booster-box", 1, 10, 0),
    ("paldea-evolved-booster-box", 1, 8, 2),
    ("prismatic-evolutions-elite-trainer-box", 3, 6, 0),
    ("surging-sparks-booster-bundle", 5, 4, 1),
    ("twilight-masquerade-booster-box", 2, 2, 0),
]


def enabled() -> bool:
    return os.getenv("DEMO_DATA", "1").strip().lower() not in ("0", "false", "no")


def month_start(today: date, months_ago: int) -> date:
    y, m = divmod(today.year * 12 + today.month - 1 - months_ago, 12)
    return date(y, m + 1, 1)


def price_series(product_id: str, current: float, release: str, today: date) -> dict:
    """Deterministic monthly prices ending at today's price (walks backwards in log space)."""
    rng = random.Random(zlib.crc32(product_id.encode()))
    drift, vol = VINTAGE if release < "2010" else MODERN
    released = date.fromisoformat(release)
    prices = {today: round(current, 2)}
    price = current
    for k in range(1, HISTORY_MONTHS + 1):
        d = month_start(today, k - 1)
        if d >= today:
            continue
        if d < released:
            break
        price = price / math.exp(drift + vol * rng.gauss(0, 1))
        prices[d] = round(price, 2)
    return prices


def seed_demo() -> None:
    conn = get_db()
    today = date.today()

    products = conn.execute("SELECT id, market_value, release_date FROM products WHERE market_value IS NOT NULL").fetchall()
    history = {}
    for p in products:
        series = price_series(p["id"], p["market_value"], p["release_date"], today)
        history[p["id"]] = series
        conn.executemany(
            "INSERT OR REPLACE INTO price_history (product_id, recorded_on, market_value) VALUES (?, ?, ?)",
            [(p["id"], d.isoformat(), v) for d, v in series.items()],
        )

    category_ids = []
    for name, description in CATEGORIES:
        conn.execute("INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)", (name, description))
        category_ids.append(conn.execute("SELECT id FROM categories WHERE name = ?", (name,)).fetchone()[0])

    rng = random.Random(42)
    for product_id, qty, months_ago, cat in COLLECTION:
        series = history.get(product_id)
        if not series:
            continue
        bought = month_start(today, months_ago)
        # Price on (or the first recorded date after) the purchase date, with a small discount or premium.
        on_or_after = sorted(d for d in series if d >= bought)
        reference = series[on_or_after[0]] if on_or_after else series[today]
        paid = round(reference * rng.uniform(0.88, 1.04), 2)
        purchase_day = bought.replace(day=min(28, 3 + rng.randrange(20)))
        conn.execute(
            "INSERT INTO items (product_id, category_id, quantity, purchase_price, purchase_date) VALUES (?, ?, ?, ?, ?)",
            (product_id, category_ids[cat], qty, paid, purchase_day.isoformat()),
        )

    conn.commit()
    conn.close()
    print(f"✅ Seeded demo price history and {len(COLLECTION)} sample holdings")
