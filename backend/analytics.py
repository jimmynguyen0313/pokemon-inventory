"""Portfolio analytics: totals, gain/loss, allocation and value over time.

Aggregation is pushed into SQLite (SUM / GROUP BY), so Python only touches
a handful of grouped rows instead of every holding:

* summary(): one aggregate query per breakdown; top movers via ORDER BY + LIMIT.
* history(): holdings are grouped by product and purchase month first
  (≈ products × months rows instead of one row per holding), then each
  group is valued at every month using a binary search over its price history.
"""

from bisect import bisect_left, bisect_right
from collections import defaultdict
from datetime import date
from sqlite3 import Connection

# Market value falls back to what was paid when a product has no price yet.
UNIT_VALUE = "COALESCE(p.market_value, i.purchase_price)"
FROM_ITEMS = "FROM items i JOIN products p ON p.id = i.product_id"


def _pct(gain: float, cost: float):
    return round(gain / cost * 100, 2) if cost else None


def _breakdown(conn: Connection, column: str, fallback: str, grand_total: float, top: int = 6) -> list:
    rows = conn.execute(f"""
        SELECT COALESCE({column}, '{fallback}') AS label, SUM({UNIT_VALUE} * i.quantity) AS value
        {FROM_ITEMS} GROUP BY label ORDER BY value DESC
    """).fetchall()
    head = [(r["label"], r["value"]) for r in rows[:top]]
    if len(rows) > top:
        head.append(("Other", sum(r["value"] for r in rows[top:])))
    return [
        {"label": label, "value": round(v, 2), "share": round(v / grand_total * 100, 1) if grand_total else 0}
        for label, v in head
    ]


def _movers(conn: Connection, order: str, where: str = "") -> list:
    rows = conn.execute(f"""
        SELECT i.id AS item_id, p.name,
               ({UNIT_VALUE} - i.purchase_price) * i.quantity AS gain,
               ({UNIT_VALUE} - i.purchase_price) * 100.0 / i.purchase_price AS gain_pct
        {FROM_ITEMS}
        WHERE i.purchase_price > 0 {where}
        ORDER BY gain_pct {order}, i.id LIMIT 3
    """).fetchall()
    return [{"item_id": r["item_id"], "name": r["name"], "gain": round(r["gain"], 2),
             "gain_pct": round(r["gain_pct"], 2)} for r in rows]


def summary(conn: Connection) -> dict:
    t = conn.execute(f"""
        SELECT COUNT(*) AS holdings,
               COALESCE(SUM(i.quantity), 0) AS units,
               COALESCE(SUM({UNIT_VALUE} * i.quantity), 0) AS market,
               COALESCE(SUM(i.purchase_price * i.quantity), 0) AS cost
        {FROM_ITEMS}
    """).fetchone()
    market, cost = t["market"], t["cost"]
    gain = market - cost
    return {
        "market_value": round(market, 2),
        "cost_basis": round(cost, 2),
        "unrealized_gain": round(gain, 2),
        "unrealized_gain_pct": _pct(gain, cost),
        "holdings": t["holdings"],
        "units": t["units"],
        "by_type": _breakdown(conn, "p.product_type", "Other", market),
        "by_set": _breakdown(conn, "p.set_name", "Unknown", market),
        "top_gainers": _movers(conn, "DESC"),
        "top_losers": _movers(conn, "ASC", f"AND {UNIT_VALUE} < i.purchase_price"),
        "as_of": date.today().isoformat(),
    }


def _month_starts(today: date, months: int) -> list[date]:
    """First day of each of the last `months` - 1 months, plus today."""
    points = []
    for k in range(months - 1, 0, -1):
        y, m = divmod(today.year * 12 + today.month - 1 - k, 12)
        points.append(date(y, m + 1, 1))
    points.append(today)
    return points


def history(conn: Connection, months: int = 12) -> list[dict]:
    """Portfolio market value and cost basis at the start of each month."""
    keys = [d.isoformat() for d in _month_starts(date.today(), months)]

    # Collapse holdings: same product bought on the same day → one row (done in SQL),
    # then bucket by the first chart point on or after the purchase date.
    groups = defaultdict(lambda: [0, 0.0])  # (product_id, first_point) → [units, cost]
    for r in conn.execute("""
        SELECT product_id, purchase_date, SUM(quantity) AS units, SUM(purchase_price * quantity) AS cost
        FROM items GROUP BY product_id, purchase_date
    """):
        first = bisect_left(keys, r["purchase_date"])
        if first < len(keys):
            g = groups[(r["product_id"], first)]
            g[0] += r["units"]
            g[1] += r["cost"]
    if not groups:
        return []

    prices = defaultdict(lambda: ([], []))
    for r in conn.execute("""
        SELECT product_id, recorded_on, market_value FROM price_history
        WHERE product_id IN (SELECT DISTINCT product_id FROM items)
        ORDER BY product_id, recorded_on
    """):
        dates, values = prices[r["product_id"]]
        dates.append(r["recorded_on"])
        values.append(r["market_value"])

    value = [0.0] * len(keys)
    cost = [0.0] * len(keys)
    for (product_id, first), (units, paid) in groups.items():
        dates, values = prices.get(product_id, ([], []))
        avg_paid = paid / units
        for i in range(first, len(keys)):
            j = bisect_right(dates, keys[i]) - 1
            # Latest price on or before this point; before any record, use what was paid.
            value[i] += (values[j] if j >= 0 else avg_paid) * units
            cost[i] += paid

    return [
        {"date": k, "market_value": round(v, 2), "cost_basis": round(c, 2)}
        for k, v, c in zip(keys, value, cost)
    ]
