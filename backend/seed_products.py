"""
Seed the database with popular Pokemon sealed products.
This allows testing without relying on external APIs.
"""

from backend.database import get_db
from datetime import date, datetime

POKEMON_PRODUCTS = [
    {
        "id": "scarlet-violet-booster-box",
        "name": "Pokémon Scarlet & Violet Booster Box",
        "product_type": "Booster Box",
        "market_value": 95.00,
        "description": "36 packs per box",
        "images_url": None,
        "set_name": "Scarlet & Violet",
        "release_date": "2023-03-31"
    },
    {
        "id": "crown-zenith-elite-trainer-box",
        "name": "Pokémon Crown Zenith Elite Trainer Box",
        "product_type": "Elite Trainer Box",
        "market_value": 35.00,
        "description": "1 booster pack",
        "images_url": None,
        "set_name": "Crown Zenith",
        "release_date": "2023-11-03"
    },
    {
        "id": "base-set-booster-box",
        "name": "Pokémon Base Set Booster Box (Shadowless)",
        "product_type": "Booster Box",
        "market_value": 7500.00,
        "description": "36 packs - Vintage",
        "images_url": None,
        "set_name": "Base Set",
        "release_date": "1999-01-09"
    },
    {
        "id": "jungle-set-booster-box",
        "name": "Pokémon Jungle Set Booster Box",
        "product_type": "Booster Box",
        "market_value": 2800.00,
        "description": "36 packs - Vintage",
        "images_url": None,
        "set_name": "Jungle",
        "release_date": "1999-06-16"
    },
    {
        "id": "sword-shield-booster-box",
        "name": "Pokémon Sword & Shield Booster Box",
        "product_type": "Booster Box",
        "market_value": 85.00,
        "description": "36 packs",
        "images_url": None,
        "set_name": "Sword & Shield",
        "release_date": "2020-02-07"
    },
    {
        "id": "brilliant-stars-booster-box",
        "name": "Pokémon Brilliant Stars Booster Box",
        "product_type": "Booster Box",
        "market_value": 92.00,
        "description": "36 packs",
        "images_url": None,
        "set_name": "Brilliant Stars",
        "release_date": "2022-02-25"
    },
    {
        "id": "paldea-evolved-booster-box",
        "name": "Pokémon Paldea Evolved Booster Box",
        "product_type": "Booster Box",
        "market_value": 98.00,
        "description": "36 packs",
        "images_url": None,
        "set_name": "Paldea Evolved",
        "release_date": "2023-06-09"
    },
    {
        "id": "obsidian-flames-booster-box",
        "name": "Pokémon Obsidian Flames Booster Box",
        "product_type": "Booster Box",
        "market_value": 96.00,
        "description": "36 packs",
        "images_url": None,
        "set_name": "Obsidian Flames",
        "release_date": "2023-08-18"
    },
    {
        "id": "temporal-forces-booster-box",
        "name": "Pokémon Temporal Forces Booster Box",
        "product_type": "Booster Box",
        "market_value": 95.00,
        "description": "36 packs",
        "images_url": None,
        "set_name": "Temporal Forces",
        "release_date": "2024-01-12"
    },
    {
        "id": "twilight-masquerade-booster-box",
        "name": "Pokémon Twilight Masquerade Booster Box",
        "product_type": "Booster Box",
        "market_value": 95.00,
        "description": "36 packs",
        "images_url": None,
        "set_name": "Twilight Masquerade",
        "release_date": "2024-05-24"
    },
    {
        "id": "evolving-skies-booster-box",
        "name": "Pokémon Evolving Skies Booster Box",
        "product_type": "Booster Box",
        "market_value": 780.00,
        "description": "36 packs",
        "images_url": None,
        "set_name": "Evolving Skies",
        "release_date": "2021-08-27"
    },
    {
        "id": "sv151-booster-bundle",
        "name": "Pokémon Scarlet & Violet 151 Booster Bundle",
        "product_type": "Booster Bundle",
        "market_value": 52.00,
        "description": "6 packs",
        "images_url": None,
        "set_name": "Scarlet & Violet 151",
        "release_date": "2023-09-22"
    },
    {
        "id": "surging-sparks-booster-bundle",
        "name": "Pokémon Surging Sparks Booster Bundle",
        "product_type": "Booster Bundle",
        "market_value": 38.00,
        "description": "6 packs",
        "images_url": None,
        "set_name": "Surging Sparks",
        "release_date": "2024-11-08"
    },
    {
        "id": "prismatic-evolutions-elite-trainer-box",
        "name": "Pokémon Prismatic Evolutions Elite Trainer Box",
        "product_type": "Elite Trainer Box",
        "market_value": 110.00,
        "description": "9 packs",
        "images_url": None,
        "set_name": "Prismatic Evolutions",
        "release_date": "2025-01-17"
    },
    {
        "id": "charizard-ultra-premium-collection",
        "name": "Pokémon Charizard Ultra-Premium Collection",
        "product_type": "Premium Collection",
        "market_value": 260.00,
        "description": "16 packs plus promos",
        "images_url": None,
        "set_name": "Sword & Shield",
        "release_date": "2022-10-07"
    },
]

def seed_db():
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    
    print(f"📦 Seeding {len(POKEMON_PRODUCTS)} Pokemon products...")
    
    for product in POKEMON_PRODUCTS:
        cursor.execute("""
            INSERT OR REPLACE INTO products 
            (id, name, product_type, market_value, description, images_url, set_name, release_date, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            product["id"],
            product["name"],
            product["product_type"],
            product["market_value"],
            product["description"],
            product["images_url"],
            product["set_name"],
            product["release_date"],
            now,
        ))
    
        # Record today's price so value-over-time charts have a current point.
        cursor.execute(
            "INSERT OR REPLACE INTO price_history (product_id, recorded_on, market_value) VALUES (?, ?, ?)",
            (product["id"], date.today().isoformat(), product["market_value"]),
        )

    conn.commit()
    conn.close()
    print(f"✅ Seeded {len(POKEMON_PRODUCTS)} products!")

if __name__ == "__main__":
    seed_db()
