# Load the raw food JSON files into a Postgres database.

import os
import json
import glob
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

if not all([DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD]):
    print("ERROR: Missing database settings. Check your .env file.")
    exit()

print("Connecting to Postgres...")
conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
)
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        code TEXT PRIMARY KEY,
        product_name TEXT,
        brands TEXT,
        categories TEXT,
        nutriscore_grade TEXT,
        nova_group INTEGER,
        energy_kcal_100g REAL,
        sugars_100g REAL,
        fat_100g REAL,
        salt_100g REAL,
        proteins_100g REAL,
        ingredients_text TEXT
    )
""")
conn.commit()

files = glob.glob("data/raw/**/*.json", recursive=True)
print("Found", len(files), "files to load")

inserted = 0
for filepath in files:
    with open(filepath) as f:
        data = json.load(f)

    products = data.get("products", [])
    for p in products:
        # every product needs a code to be the primary key.
        if not p.get("code"):
            continue
        nutriments = p.get("nutriments", {})
        categories = ", ".join(p.get("categories_tags", []))

        cur.execute("""
            INSERT INTO products (
                code, product_name, brands, categories, nutriscore_grade,
                nova_group, energy_kcal_100g, sugars_100g, fat_100g,
                salt_100g, proteins_100g, ingredients_text
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (code) DO UPDATE SET
                product_name = EXCLUDED.product_name,
                brands = EXCLUDED.brands,
                categories = EXCLUDED.categories,
                nutriscore_grade = EXCLUDED.nutriscore_grade,
                nova_group = EXCLUDED.nova_group,
                energy_kcal_100g = EXCLUDED.energy_kcal_100g,
                sugars_100g = EXCLUDED.sugars_100g,
                fat_100g = EXCLUDED.fat_100g,
                salt_100g = EXCLUDED.salt_100g,
                proteins_100g = EXCLUDED.proteins_100g,
                ingredients_text = EXCLUDED.ingredients_text
        """, (
            p.get("code"),
            p.get("product_name"),
            p.get("brands"),
            categories,
            p.get("nutriscore_grade"),
            p.get("nova_group"),
            nutriments.get("energy-kcal_100g"),
            nutriments.get("sugars_100g"),
            nutriments.get("fat_100g"),
            nutriments.get("salt_100g"),
            nutriments.get("proteins_100g"),
            p.get("ingredients_text"),
        ))
        inserted += 1

conn.commit()
print("Loaded", inserted, "products into the database.")

cur.close()
conn.close()
print("Done!")