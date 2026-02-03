# Copilot Instructions for Pokemon Inventory

## Architecture Overview

**React + FastAPI full-stack application** for managing Pokemon sealed collection inventory with valuation tracking.

### Technology Stack
- **Frontend**: React 19 with Create React App (port 3000)
- **Backend**: FastAPI with SQLite (port 8000)
- **External API**: Pokemon Price Tracker API (https://pokemonpricetracker.com/api) - requires `POKEMON_PRICE_TRACKER_API_KEY` environment variable
- **Database**: SQLite3 with `products` (cached from API) and `items` (user inventory) tables

### Project Structure

**Backend** ([backend/](../backend/))
- `app.py` - FastAPI server with 5 endpoints: `GET /products/search`, `GET /products/{id}`, `GET /products`, `POST /products/sync`, `POST/GET /items`, `GET /total-value`
- `pokemon_api.py` - Pokemon Price Tracker API client (`fetch_products`, `get_product_by_id`, `sync_products_to_db`)
- `models.py` - Pydantic schemas: `ItemCreate` (product_id, quantity, purchase_price, category), `ProductCreate`
- `database.py` - SQLite connection manager
- `db_init.py` - Schema initialization (products table + items table with FK, indexes on name/product_type/product_id)
- `sync_products.py` - CLI script to bulk sync products from Pokemon Price Tracker

**Frontend** ([src/](../src/))
- `App.js` - Main orchestrator with state (selectedProduct, refreshInventory trigger)
- Components: `ProductSearch.js` (debounced search), `AddItem.js` (form), `InventoryList.js` (grid), `PortfolioValue.js` (dashboard)

## Critical Setup & API

### Initial Setup
```bash
# 1. Get free API key: https://www.pokemonpricetracker.com/api
# 2. Backend setup
cd backend
pip install -r requirements.txt
export POKEMON_PRICE_TRACKER_API_KEY=your_key  # Must set before running
python db_init.py
python sync_products.py --limit 250  # Initial seed

# 3. Frontend
npm install
```

### Running Locally
```bash
# Terminal 1: Backend (port 8000, http://localhost:8000/docs for Swagger)
cd backend && uvicorn app:app --reload

# Terminal 2: Frontend (port 3000)
npm start
```

### Key Endpoint Behaviors
- `GET /products/search?name=...` - Queries LOCAL database (instant), limited to 50 results
- `POST /products/sync` - Fetches up to 100 products from Pokemon Price Tracker API, upserts to DB
- `POST /items` - Validates product_id exists, sets purchase_date to today automatically
- `GET /items` - Returns LEFT JOIN (items + products), includes market_value and set_name for display
- `GET /total-value` - Sums (market_value OR purchase_price) * quantity across all items

## Data & API Patterns

### Database Schema (Optimized)
**Products Table**
- `id` (TEXT PK): Unique product identifier
- `name` (TEXT NOT NULL, COLLATE NOCASE): Product name with case-insensitive collation for efficient searches
- `product_type` (TEXT NOT NULL): Type classification (e.g., "Booster", "Elite Trainer Box")
- `market_value` (REAL CHECK >= 0): Current market pricing with CHECK constraint
- `description`, `images_url`, `set_name`, `release_date` (TEXT): Metadata from Pokemon Price Tracker
- `created_at`, `last_updated` (TIMESTAMP): Automatic timestamps for sync tracking
- **Indexes**: `idx_products_name`, `idx_products_type`, `idx_products_last_updated DESC`

**Items Table**
- `id` (INTEGER PK AUTOINCREMENT): Unique inventory item ID
- `product_id` (TEXT FK NOT NULL): References `products.id` with ON DELETE RESTRICT
- `category_id` (INTEGER FK): Optional reference to `categories.id` with ON DELETE SET NULL
- `quantity` (INTEGER NOT NULL, CHECK > 0): Quantity with validation
- `purchase_price` (REAL NOT NULL, CHECK >= 0): Purchase cost with validation
- `purchase_date` (DATE NOT NULL, DEFAULT CURRENT_DATE): When item was acquired
- `created_at`, `updated_at` (TIMESTAMP): Audit timestamps
- **Indexes**: `idx_items_product_id`, `idx_items_category_id`, `idx_items_purchase_date DESC`, composite `idx_items_product_quantity`

**Categories Table**
- `id` (INTEGER PK AUTOINCREMENT): Category identifier
- `name` (TEXT UNIQUE NOT NULL): Category name (e.g., "Sealed Boxes", "Graded Cards")
- `description` (TEXT): Optional category description
- Normalizes item categories for efficient filtering and constraint enforcement

### Critical Performance Patterns
1. **PRAGMA foreign_keys = ON** - Enforced at connection time in `db_init.py` for referential integrity
2. **Parameterized Queries** - All endpoints use `?` placeholders to prevent SQL injection
3. **Composite Indexes** - `idx_items_product_quantity` for common aggregation queries (valuation calculations)
4. **COLLATE NOCASE** - Product name searches are case-insensitive without functions
5. **CHECK Constraints** - Values validated at database level (e.g., quantity > 0, prices >= 0)
6. **Date Columns** - DATE and TIMESTAMP types for efficient temporal queries vs. TEXT
7. **Foreign Key Constraints** - ON DELETE RESTRICT (products) and ON DELETE SET NULL (categories) prevent data inconsistency

### Optimized Query Patterns
- **Search**: Uses indexed COLLATE NOCASE for case-insensitive matching without LOWER()
- **Aggregations**: Composite index `idx_items_product_quantity` optimizes portfolio value calculations
- **Sorting**: `idx_items_purchase_date DESC` for reverse-chronological ordering
- **Joins**: LEFT JOIN with categories ensures category deletions don't break inventory

### API Endpoints with Schema Validation
- `POST /items` - Validates product_id + category_id exist, returns item_id
- `POST /categories` - Creates unique category, enforces unique constraint
- `GET /categories` - Lists all categories for UI dropdowns
- `GET /items` - Returns full inventory with product names, market values, category names
- Pydantic validation: `quantity: int = Field(gt=0)`, `purchase_price: float = Field(ge=0)`

### Frontend State Management
- `selectedProduct` state - Tracks user selection from ProductSearch, passed to AddItem form
- `refreshInventory` counter - Incremented in handleItemAdded to trigger InventoryList + PortfolioValue re-fetch
- ProductSearch debounces 300ms to reduce `/products/search` calls

## Important Notes
- **Environment Variable Required**: `POKEMON_PRICE_TRACKER_API_KEY` must be set before backend startup; API client prints helpful error if missing
- **CORS Wide Open** - `allow_origins=["*"]` for dev (restrict before production)
- **No Pagination** - `/items` and `/products` return all records
- **Auto purchase_date** - Set by `date('now')` in SQL INSERT
- **No Authentication** - All endpoints public
- **SQLite Limitations** - Basic locking; sync writes may block reads briefly


