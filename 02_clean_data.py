"""
01_generate_raw_data.py
------------------------
Generates a synthetic, intentionally messy e-commerce sales dataset.
This simulates the kind of raw export a client might hand over:
missing values, duplicate rows, inconsistent casing/date formats,
currency symbols in numeric fields, and a few outliers.

Run: python 01_generate_raw_data.py
Output: ../data/raw_sales_data.csv
"""

import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

N_ROWS = 1200

regions = ["Gauteng", "Western Cape", "KwaZulu-Natal", "Eastern Cape", "Free State"]
region_variants = {
    "Gauteng": ["Gauteng", "gauteng", "GAUTENG", "Guateng"],
    "Western Cape": ["Western Cape", "western cape", "W. Cape", "WESTERN CAPE"],
    "KwaZulu-Natal": ["KwaZulu-Natal", "kwazulu natal", "KZN", "Kwazulu-Natal"],
    "Eastern Cape": ["Eastern Cape", "eastern cape", "E. Cape", "EASTERN CAPE"],
    "Free State": ["Free State", "free state", "FREE STATE", "Free  State"],
}

products = [
    ("Wireless Mouse", 249.99, "Electronics"),
    ("Bluetooth Speaker", 599.00, "Electronics"),
    ("Office Chair", 1499.00, "Furniture"),
    ("Standing Desk", 3299.00, "Furniture"),
    ("Notebook Set", 89.99, "Stationery"),
    ("LED Desk Lamp", 349.50, "Home"),
    ("USB-C Hub", 429.00, "Electronics"),
    ("Yoga Mat", 279.00, "Fitness"),
    ("Water Bottle", 149.00, "Fitness"),
    ("Backpack", 899.00, "Accessories"),
]

sales_reps = ["T. Nkosi", "L. van der Merwe", "S. Dlamini", "R. Naidoo", "M. Botha"]

date_formats = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"]

rows = []
start_date = datetime(2025, 1, 1)

for i in range(N_ROWS):
    order_id = f"ORD{10000 + i}"
    product_name, base_price, category = random.choice(products)
    region_clean = random.choice(regions)
    region_display = random.choice(region_variants[region_clean])

    qty = random.choice([1, 1, 1, 2, 2, 3, 5, 10])
    unit_price = base_price * random.uniform(0.95, 1.05)

    # Introduce currency symbol / string formatting messiness ~30% of the time
    if random.random() < 0.3:
        price_str = f"R {unit_price:,.2f}"
    else:
        price_str = round(unit_price, 2)

    order_date = start_date + timedelta(days=random.randint(0, 364))
    date_str = order_date.strftime(random.choice(date_formats))

    rep = random.choice(sales_reps)

    row = {
        "OrderID": order_id,
        "OrderDate": date_str,
        "Region": region_display,
        "Product": product_name,
        "Category": category,
        "Quantity": qty,
        "UnitPrice": price_str,
        "SalesRep": rep,
    }
    rows.append(row)

df = pd.DataFrame(rows)

# Inject missing values (~5% of Quantity and ~4% of UnitPrice)
for col, frac in [("Quantity", 0.05), ("UnitPrice", 0.04), ("Region", 0.02)]:
    idx = df.sample(frac=frac, random_state=1).index
    df.loc[idx, col] = np.nan

# Inject a handful of duplicate rows
dupes = df.sample(15, random_state=2)
df = pd.concat([df, dupes], ignore_index=True)

# Inject a few extreme outliers in Quantity (data entry errors)
outlier_idx = df.sample(5, random_state=3).index
df.loc[outlier_idx, "Quantity"] = df.loc[outlier_idx, "Quantity"].apply(
    lambda x: 500 if pd.notna(x) else x
)

# Shuffle rows
df = df.sample(frac=1, random_state=4).reset_index(drop=True)

df.to_csv("../data/raw_sales_data.csv", index=False)
print(f"Generated {len(df)} rows -> data/raw_sales_data.csv")
