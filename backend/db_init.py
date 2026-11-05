from backend.database import DB_PATH
import sqlite3

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")  # Enforce foreign key constraints
    
    # Categories lookup table - normalize category data
    conn.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT
    )
    """)
    
    # Products table - cached from Pokemon Price Tracker API
    # Optimized with constraints, proper types, and timestamps
    conn.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL COLLATE NOCASE,
        product_type TEXT NOT NULL,
        market_value REAL CHECK(market_value IS NULL OR market_value >= 0),
        description TEXT,
        images_url TEXT,
        set_name TEXT,
        release_date DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
    )
    """)
    
    # Items table - user's inventory with referential integrity
    conn.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id TEXT NOT NULL,
        category_id INTEGER,
        quantity INTEGER NOT NULL DEFAULT 1 CHECK(quantity > 0),
        purchase_price REAL NOT NULL CHECK(purchase_price >= 0),
        purchase_date DATE NOT NULL DEFAULT CURRENT_DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT,
        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
    )
    """)
    
    # Composite indexes for common query patterns
    conn.execute("CREATE INDEX IF NOT EXISTS idx_products_name ON products(name)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_products_type ON products(product_type)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_products_last_updated ON products(last_updated DESC)")
    
    # Items indexes for filtering and joins
    conn.execute("CREATE INDEX IF NOT EXISTS idx_items_product_id ON items(product_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_items_category_id ON items(category_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_items_purchase_date ON items(purchase_date DESC)")
    
    # Composite index for common aggregation queries
    conn.execute("CREATE INDEX IF NOT EXISTS idx_items_product_quantity ON items(product_id, quantity)")
    
    conn.commit()
    conn.close()
    print("✅ DB initialized at", DB_PATH)

if __name__ == "__main__":
    init_db()
