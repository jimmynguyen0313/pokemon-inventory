import requests
from datetime import datetime
from typing import Optional, List, Dict
import os

BASE_URL = "https://www.pokemonpricetracker.com/api/v2"
REQUEST_TIMEOUT = 30

# Get API key from environment variable
API_KEY = os.getenv("POKEMON_PRICE_TRACKER_API_KEY", "")

def fetch_products(query: str = "", product_type: str = "") -> List[Dict]:
    """
    Fetch Pokemon sealed products from Pokemon Price Tracker API.
    
    Args:
        query: Search query for product name
        product_type: Filter (not used, kept for compatibility)
    
    Returns:
        List of product dictionaries with id, name, product_type, market_value, description, images_url
    """
    if not API_KEY:
        print("❌ POKEMON_PRICE_TRACKER_API_KEY environment variable not set. Get free key at https://www.pokemonpricetracker.com/api")
        return []
    
    try:
        headers = {"Authorization": f"Bearer {API_KEY}"}
        params = {
            "search": query if query else "booster",
            "limit": 100,
        }
        
        response = requests.get(
            f"{BASE_URL}/sealed-products",
            params=params,
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        
        data = response.json()
        products = []
        
        for product in data.get("data", []):
            products.append({
                "id": str(product.get("id")),
                "name": product.get("name", ""),
                "product_type": product.get("productType", "Sealed"),
                "market_value": product.get("prices", {}).get("market"),
                "description": product.get("setName", ""),
                "images_url": product.get("imageCdnUrl"),
                "set_name": product.get("setName", ""),
                "release_date": product.get("releaseDate", ""),
            })
        
        return products
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching from Pokemon Price Tracker API: {e}")
        return []


def get_product_by_id(product_id: str) -> Optional[Dict]:
    """Fetch a single product by ID from Pokemon Price Tracker API."""
    if not API_KEY:
        print("❌ POKEMON_PRICE_TRACKER_API_KEY environment variable not set")
        return None
    
    try:
        headers = {"Authorization": f"Bearer {API_KEY}"}
        response = requests.get(
            f"{BASE_URL}/sealed-products/{product_id}",
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        
        product = response.json().get("data", {})
        return {
            "id": str(product.get("id")),
            "name": product.get("name", ""),
            "product_type": product.get("productType", "Sealed"),
            "market_value": product.get("prices", {}).get("market"),
            "description": product.get("setName", ""),
            "images_url": product.get("imageCdnUrl"),
            "set_name": product.get("setName", ""),
            "release_date": product.get("releaseDate", ""),
        }
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching product {product_id}: {e}")
        return None


def sync_products_to_db(conn, limit: int = 100) -> int:
    """
    Sync Pokemon sealed products from Pokemon Price Tracker API to local database.
    
    Args:
        conn: SQLite connection
        limit: Max number of products to fetch
    
    Returns:
        Number of products synced
    """
    if not API_KEY:
        print("❌ POKEMON_PRICE_TRACKER_API_KEY environment variable not set")
        print("   Get your free API key at: https://www.pokemonpricetracker.com/api")
        print("   Then set it: export POKEMON_PRICE_TRACKER_API_KEY=your_key_here")
        return 0
    
    try:
        print(f"⏳ Fetching Pokemon sealed products from Pokemon Price Tracker...")
        
        headers = {"Authorization": f"Bearer {API_KEY}"}
        params = {
            "search": "booster",
            "limit": limit,
        }
        
        response = requests.get(
            f"{BASE_URL}/sealed-products",
            params=params,
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        
        products = response.json().get("data", [])
        now = datetime.now().isoformat()
        cursor = conn.cursor()
        synced_count = 0
        
        print(f"📦 Inserting {len(products)} products into database...")
        for product in products:
            cursor.execute("""
                INSERT OR REPLACE INTO products 
                (id, name, product_type, market_value, description, images_url, set_name, release_date, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(product.get("id")),
                product.get("name", ""),
                product.get("productType", "Sealed"),
                product.get("prices", {}).get("market"),
                product.get("setName", ""),
                product.get("imageCdnUrl"),
                product.get("setName", ""),
                product.get("releaseDate", ""),
                now,
            ))
            market = product.get("prices", {}).get("market")
            if market is not None:
                cursor.execute(
                    "INSERT OR REPLACE INTO price_history (product_id, recorded_on, market_value) VALUES (?, ?, ?)",
                    (str(product.get("id")), now[:10], market),
                )
            synced_count += 1
        
        conn.commit()
        return synced_count
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error syncing products: {e}")
        return 0



