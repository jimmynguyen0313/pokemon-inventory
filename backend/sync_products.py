"""
Sync Pokemon products from the Pokemon TCG API to local SQLite database.
Run this script periodically to keep product data fresh.

Usage: python sync_products.py [--limit N]
    --limit N: Number of products to fetch (default: 100)
"""

import argparse
from backend.database import get_db
from backend.pokemon_api import sync_products_to_db

def main():
    parser = argparse.ArgumentParser(description="Sync Pokemon products from TCG API")
    parser.add_argument("--limit", type=int, default=100, help="Max products to sync")
    args = parser.parse_args()
    
    conn = get_db()
    synced = sync_products_to_db(conn, limit=args.limit)
    conn.close()
    
    print(f"✅ Synced {synced} products from Pokemon TCG API")

if __name__ == "__main__":
    main()
