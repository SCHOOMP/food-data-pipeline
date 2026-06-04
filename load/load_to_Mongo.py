import os
import json
import glob
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")

# stop if settings are missing
if not all([MONGO_USER, MONGO_PASSWORD]):
    print("ERROR: Missing MongoDB settings. Check your .env file.")
    exit()

# build the connection string. authSource=admin is where the root user lives.
uri = "mongodb://" + MONGO_USER + ":" + MONGO_PASSWORD + "@" + MONGO_HOST + ":" + MONGO_PORT + "/?authSource=admin"

print("Connecting to MongoDB...")
client = MongoClient(uri)
client.admin.command("ping")   # fail fast with a clear error if it can't connect

# a "database" holds "collections", which hold "documents" (like JSON objects)
db = client["fooddata"]
collection = db["products_raw"]

# find all the JSON files I saved in data/raw
files = glob.glob("data/raw/**/*.json", recursive=True)
print("Found", len(files), "files to load")

inserted = 0
for filepath in files:
    with open(filepath) as f:
        data = json.load(f)

    products = data.get("products", [])
    for p in products:
        if not p.get("code"):
            continue

        # use the product's barcode as the document id (_id). then replace_one
        # with upsert=True means: if it's already there, replace it; if not, add it.
        # same idea as ON CONFLICT in Postgres - safe to run again.
        p["_id"] = p["code"]
        collection.replace_one({"_id": p["_id"]}, p, upsert=True)
        inserted += 1

print("Loaded", inserted, "products into MongoDB.")
client.close()
print("Done!")