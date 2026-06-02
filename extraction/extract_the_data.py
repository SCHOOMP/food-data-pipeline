# Get food data from the Open Food Facts API and save it as JSON files.
# This is the first step of my pipeline - just grabbing the raw data.

import requests
import json
import time
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

CATEGORY = "breakfast-cereals"
MAX_PAGES = 3
PAGE_SIZE = 100
DELAY = 6
#Grabbing Email From Evn file
EMAIL = os.getenv("OFF_EMAIL")

if not EMAIL:
    print("ERROR: No email found.")
    exit()

USER_AGENT = "food-data-pipeline/0.1 (" + EMAIL + ")"

URL = "https://world.openfoodfacts.org/api/v2/search"

# the fields I want back for each product
fields = "code,product_name,brands,categories_tags,nutriscore_grade,nova_group,ingredients_text,nutriments"

# make a folder to save the data in
now = datetime.now().strftime("%Y-%m-%d")
folder = "data/raw/" + CATEGORY + "/" + now
os.makedirs(folder, exist_ok=True)

headers = {"User-Agent": USER_AGENT}

for page in range(1, MAX_PAGES + 1):
    print("Getting page", page)

    params = {
        "categories_tags_en": CATEGORY,
        "fields": fields,
        "page": page,
        "page_size": PAGE_SIZE,
    }

    response = requests.get(URL, params=params, headers=headers)

    if response.status_code == 503:
        print("  too fast, waiting 5 seconds and trying again...")
        time.sleep(5)
        response = requests.get(URL, params=params, headers=headers)

    data = response.json()
    products = data.get("products", [])

    filename = folder + "/page_" + str(page) + ".json"
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print("  saved", len(products), "products to", filename)

    if len(products) == 0:
        print("No more products, stopping.")
        break
    time.sleep(DELAY)

print("Done!")