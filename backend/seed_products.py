"""
Seed the database with popular Pokemon sealed products.
This allows testing without relying on external APIs.
"""

from database import get_db
from datetime import datetime

POKEMON_PRODUCTS = [
    {
        "id": "scarlet-violet-booster-box",
        "name": "Pokémon Scarlet & Violet Booster Box",
        "product_type": "Booster Box",
        "market_value": 95.00,
        "description": "36 packs per box",
        "images_url": "https://d2t6xzbnpc9v9w.cloudfront.net/images/ProductImages/pokemon/sv/sv04pt5_bb.png",
        "set_name": "Scarlet & Violet",
        "release_date": "2023-03-31"
    },
    {
        "id": "crown-zenith-elite-trainer-box",
        "name": "Pokémon Crown Zenith Elite Trainer Box",
        "product_type": "Elite Trainer Box",
        "market_value": 35.00,
        "description": "1 booster pack",
        "images_url": "https://d2t6xzbnpc9v9w.cloudfront.net/images/ProductImages/pokemon/sv/sv04pt5_etb.png",
        "set_name": "Crown Zenith",
        "release_date": "2023-11-03"
    },
    {
        "id": "base-set-booster-box",
        "name": "Pokémon Base Set Booster Box (Shadowless)",
        "product_type": "Booster Box",
        "market_value": 7500.00,
        "description": "36 packs - Vintage",
        "images_url": "https://d2t6xzbnpc9v9w.cloudfront.net/images/ProductImages/pokemon/base/base1_bb.png",
        "set_name": "Base Set",
        "release_date": "1999-01-09"
    },
    {
        "id": "jungle-set-booster-box",
        "name": "Pokémon Jungle Set Booster Box",
        "product_type": "Booster Box",
        "market_value": 2800.00,
        "description": "36 packs - Vintage",
        "images_url": "https://d2t6xzbnpc9v9w.cloudfront.net/images/ProductImages/pokemon/jungle/jungle_bb.png",
        "set_name": "Jungle",
        "release_date": "1999-06-16"
    },
    {
        "id": "sword-shield-booster-box",
        "name": "Pokémon Sword & Shield Booster Box",
        "product_type": "Booster Box",
        "market_value": 85.00,
        "description": "36 packs",
        "images_url": "https://d2t6xzbnpc9v9w.cloudfront.net/images/ProductImages/pokemon/swsh/swsh1_bb.png",
        "set_name": "Sword & Shield",
        "release_date": "2020-02-07"
    },
    {
        "id": "brilliant-stars-booster-box",
        "name": "Pokémon Brilliant Stars Booster Box",
        "product_type": "Booster Box",
        "market_value": 92.00,
        "description": "36 packs",
        "images_url": "https://d2t6xzbnpc9v9w.cloudfront.net/images/ProductImages/pokemon/swsh/swsh8pt5_bb.png",
        "set_name": "Brilliant Stars",
        "release_date": "2022-02-25"
    },
    {
        "id": "paldea-evolved-booster-box",
        "name": "Pokémon Paldea Evolved Booster Box",
        "product_type": "Booster Box",
        "market_value": 98.00,
        "description": "36 packs",
        "images_url": "https://d2t6xzbnpc9v9w.cloudfront.net/images/ProductImages/pokemon/sv/sv02_bb.png",
        "set_name": "Paldea Evolved",
        "release_date": "2023-06-09"
    },
    {
        "id": "obsidian-flames-booster-box",
        "name": "Pokémon Obsidian Flames Booster Box",
        "product_type": "Booster Box",
        "market_value": 96.00,
        "description": "36 packs",
        "images_url": "https://d2t6xzbnpc9v9w.cloudfront.net/images/ProductImages/pokemon/sv/sv04_bb.png",
        "set_name": "Obsidian Flames",
        "release_date": "2023-08-18"
    },
    {
        "id": "temporal-forces-booster-box",
        "name": "Pokémon Temporal Forces Booster Box",
        "product_type": "Booster Box",
        "market_value": 95.00,
        "description": "36 packs",
        "images_url": "https://d2t6xzbnpc9v9w.cloudfront.net/images/ProductImages/pokemon/sv/sv05_bb.png",
        "set_name": "Temporal Forces",
        "release_date": "2024-01-12"
    },
    {
        "id": "twilight-masquerade-booster-box",
        "name": "Pokémon Twilight Masquerade Booster Box",
        "product_type": "Booster Box",
        "market_value": 95.00,
        "description": "36 packs",
        "images_url": "https://d2t6xzbnpc9v9w.cloudfront.net/images/ProductImages/pokemon/sv/sv06_bb.png",
        "set_name": "Twilight Masquerade",
        "release_date": "2024-05-24"
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
    
    conn.commit()
    conn.close()
    print(f"✅ Seeded {len(POKEMON_PRODUCTS)} products!")

if __name__ == "__main__":
    seed_db()
