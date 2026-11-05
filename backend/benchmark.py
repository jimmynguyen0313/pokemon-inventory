"""Measure API latency on a large synthetic collection.

    python -m backend.benchmark                  # 10,000 holdings
    python -m backend.benchmark --items 50000

Builds a throwaway database with the full catalog, 24 months of price
history and N holdings, then times each read endpoint in-process
(FastAPI TestClient, so no network overhead is included).
"""

import argparse
import os
import random
import statistics
import tempfile
import time
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--items", type=int, default=10_000)
    parser.add_argument("--runs", type=int, default=50)
    args = parser.parse_args()

    tmp = Path(tempfile.mkdtemp()) / "bench.db"
    os.environ["DEMO_DATA"] = "1"
    from backend import database
    database.DB_PATH = tmp

    from fastapi.testclient import TestClient
    from backend.app import app
    from backend.demo_data import month_start
    from datetime import date

    with TestClient(app) as client:
        conn = database.get_db()
        products = [r[0] for r in conn.execute("SELECT id FROM products")]
        rng = random.Random(0)
        today = date.today()
        conn.executemany(
            "INSERT INTO items (product_id, quantity, purchase_price, purchase_date) VALUES (?, ?, ?, ?)",
            [(rng.choice(products), rng.randint(1, 6), round(rng.uniform(20, 900), 2),
              month_start(today, rng.randrange(24)).replace(day=rng.randint(1, 28)).isoformat())
             for _ in range(args.items)],
        )
        conn.commit()
        n_items = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        n_prices = conn.execute("SELECT COUNT(*) FROM price_history").fetchone()[0]
        conn.close()
        print(f"{n_items:,} holdings · {len(products)} products · {n_prices:,} price records · {args.runs} runs each\n")

        endpoints = [
            "/analytics/summary",
            "/analytics/history?months=12",
            "/analytics/history?months=24",
            "/items",
            "/products/search?name=booster",
        ]
        print(f"{'endpoint':32s} {'p50':>8s} {'p95':>8s}")
        for url in endpoints:
            client.get(url)  # warm up
            times = []
            for _ in range(args.runs):
                start = time.perf_counter()
                response = client.get(url)
                times.append((time.perf_counter() - start) * 1000)
                assert response.status_code == 200
            times.sort()
            p95 = times[int(len(times) * 0.95) - 1]
            print(f"{url:32s} {statistics.median(times):6.1f}ms {p95:6.1f}ms")


if __name__ == "__main__":
    main()
