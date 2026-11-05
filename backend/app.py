from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.models import ItemCreate, ProductCreate, CategoryCreate, Category
from backend.database import get_db
from backend.pokemon_api import fetch_products, get_product_by_id, sync_products_to_db
from backend.db_init import init_db
from backend.seed_products import seed_db
from backend import analytics, demo_data
from contextlib import asynccontextmanager
from datetime import datetime
import os
from urllib.parse import urlsplit

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup and seed sample products into an empty database,
    # so a fresh deploy (e.g. Render's ephemeral disk) works out of the box.
    init_db()
    conn = get_db()
    product_count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    conn.close()
    if product_count == 0:
        seed_db()
        if demo_data.enabled():
            demo_data.seed_demo()
    yield

app = FastAPI(title="Pokemon Sealed Inventory API", lifespan=lifespan)

# Comma-separated list of frontend origins allowed to call the API,
# e.g. ALLOWED_ORIGINS="https://my-portfolio.vercel.app". Defaults to the local dev server.
def parse_origins(raw: str) -> list[str]:
    """Normalize to scheme://host[:port]; browsers send the origin without a path or trailing slash,
    so "https://user.github.io/app/" must become "https://user.github.io" to match."""
    origins = []
    for value in raw.split(","):
        value = value.strip().strip('"').strip("'")
        if not value:
            continue
        parts = urlsplit(value if "://" in value else f"https://{value}")
        origin = f"{parts.scheme}://{parts.netloc}".lower()
        if parts.netloc and origin not in origins:
            origins.append(origin)
    return origins

ALLOWED_ORIGINS = parse_origins(os.getenv("ALLOWED_ORIGINS", "http://localhost:3000"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)

@app.get("/health")
def health():
    """Lightweight health check for the hosting platform."""
    return {"status": "ok"}

# ============ Product Endpoints ============

@app.get("/products/search")
def search_products(name: str = Query(""), product_type: str = Query("")):
    """Search cached products in local database (instant, no API calls)."""
    conn = get_db()
    
    query = "SELECT * FROM products WHERE 1=1"
    params = []
    
    if name:
        query += " AND name LIKE ?"
        params.append(f"%{name}%")
    
    if product_type:
        query += " AND product_type LIKE ?"
        params.append(f"%{product_type}%")
    
    query += " ORDER BY name LIMIT 50"
    
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/products/{product_id}/history")
def product_history(product_id: str):
    """Recorded market prices for one product, oldest first."""
    conn = get_db()
    rows = conn.execute(
        "SELECT recorded_on AS date, market_value FROM price_history WHERE product_id = ? ORDER BY recorded_on",
        (product_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/products/{product_id}")
def get_product(product_id: str):
    """Get a specific product from TCG API."""
    product = get_product_by_id(product_id)
    if not product:
        return {"error": "Product not found"}
    return product

@app.get("/products")
def list_products():
    """List all products cached in local database."""
    conn = get_db()
    rows = conn.execute("SELECT * FROM products ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.post("/products/sync")
def sync_products():
    """Sync products from Pokemon TCG API to local database."""
    conn = get_db()
    synced_count = sync_products_to_db(conn, limit=100)
    conn.close()
    return {"status": "synced", "count": synced_count}

# ============ Inventory Endpoints ============

@app.post("/items")
def add_item(item: ItemCreate):
    """Add item to inventory. Product must exist in database."""
    conn = get_db()
    cur = conn.cursor()
    
    # Verify product exists
    product = conn.execute("SELECT id FROM products WHERE id = ?", (item.product_id,)).fetchone()
    if not product:
        conn.close()
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Verify category exists if provided
    if item.category_id:
        category = conn.execute("SELECT id FROM categories WHERE id = ?", (item.category_id,)).fetchone()
        if not category:
            conn.close()
            raise HTTPException(status_code=404, detail="Category not found")
    
    # Insert item with optimized schema
    cur.execute("""
        INSERT INTO items (product_id, category_id, quantity, purchase_price, purchase_date)
        VALUES (?, ?, ?, ?, COALESCE(?, CURRENT_DATE))
    """, (item.product_id, item.category_id, item.quantity, item.purchase_price,
          item.purchase_date.isoformat() if item.purchase_date else None))
    conn.commit()
    item_id = cur.lastrowid
    conn.close()
    return {"status": "created", "item_id": item_id, "item": item}

@app.get("/items")
def get_items():
    """Fetch all inventory items with product and category details."""
    conn = get_db()
    rows = conn.execute("""
        SELECT i.id, i.product_id, i.category_id, i.quantity, i.purchase_price, i.purchase_date,
               i.created_at, i.updated_at,
               p.name, p.product_type, p.market_value, p.images_url, p.set_name,
               c.name AS category_name,
               ROUND(i.purchase_price * i.quantity, 2) AS cost_basis,
               ROUND(COALESCE(p.market_value, i.purchase_price) * i.quantity, 2) AS market_total,
               ROUND((COALESCE(p.market_value, i.purchase_price) - i.purchase_price) * i.quantity, 2) AS gain,
               CASE WHEN i.purchase_price > 0
                    THEN ROUND((COALESCE(p.market_value, i.purchase_price) - i.purchase_price) * 100.0 / i.purchase_price, 2)
               END AS gain_pct
        FROM items i
        LEFT JOIN products p ON i.product_id = p.id
        LEFT JOIN categories c ON i.category_id = c.id
        ORDER BY i.purchase_date DESC, i.id DESC
    """).fetchall()
    conn.close()
    # Rows are already JSON-safe (str/int/float/None), so skip FastAPI's per-field
    # jsonable_encoder pass, which dominates response time for large collections.
    return JSONResponse([dict(r) for r in rows])

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    """Delete an item from inventory."""
    conn = get_db()
    cur = conn.cursor()
    
    # Verify item exists
    item = conn.execute("SELECT id FROM items WHERE id = ?", (item_id,)).fetchone()
    if not item:
        conn.close()
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Delete the item
    cur.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted", "item_id": item_id}

# ============ Category Endpoints ============

@app.post("/categories")
def create_category(category: CategoryCreate):
    """Create a new inventory category."""
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO categories (name, description)
            VALUES (?, ?)
        """, (category.name, category.description))
        conn.commit()
        category_id = cur.lastrowid
        conn.close()
        return {"status": "created", "category_id": category_id, "category": category}
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail="Category already exists or invalid data")

@app.get("/categories")
def list_categories():
    """Get all inventory categories."""
    conn = get_db()
    rows = conn.execute("""
        SELECT id, name, description FROM categories ORDER BY name
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ============ Analytics Endpoints ============

@app.get("/analytics/summary")
def analytics_summary():
    """Totals, unrealized gain/loss, allocation and top movers."""
    conn = get_db()
    try:
        return analytics.summary(conn)
    finally:
        conn.close()

@app.get("/analytics/history")
def analytics_history(months: int = Query(12, ge=2, le=60)):
    """Portfolio market value and cost basis at the start of each month."""
    conn = get_db()
    try:
        return analytics.history(conn, months)
    finally:
        conn.close()
