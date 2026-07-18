"""
02_clean_data.py
-----------------
Cleans the raw sales export:
 - Standardises Region names (casing, typos, spacing)
 - Parses inconsistent date formats into a single datetime format
 - Strips currency symbols / commas from UnitPrice and converts to float
 - Removes exact duplicate rows
 - Handles missing values (impute Quantity/UnitPrice with category median,
   drop rows with missing Region since it can't be reasonably inferred)
 - Flags and caps extreme outliers in Quantity (data entry errors)
 - Adds a computed Revenue column (Quantity * UnitPrice)

Run: python 02_clean_data.py
Input:  ../data/raw_sales_data.csv
Output: ../data/cleaned_sales_data.csv
"""

import re
import pandas as pd
import numpy as np

df = pd.read_csv("../data/raw_sales_data.csv")
initial_rows = len(df)

# --- 1. Remove exact duplicates ---
df = df.drop_duplicates()

# --- 2. Standardise Region ---
region_map = {
    "gauteng": "Gauteng", "guateng": "Gauteng",
    "western cape": "Western Cape", "w. cape": "Western Cape",
    "kwazulu-natal": "KwaZulu-Natal", "kwazulu natal": "KwaZulu-Natal", "kzn": "KwaZulu-Natal",
    "eastern cape": "Eastern Cape", "e. cape": "Eastern Cape",
    "free state": "Free State", "free  state": "Free State",
}

def clean_region(val):
    if pd.isna(val):
        return np.nan
    key = re.sub(r"\s+", " ", str(val)).strip().lower()
    return region_map.get(key, str(val).strip())

df["Region"] = df["Region"].apply(clean_region)

# Drop rows with no region — can't reliably impute geography
df = df.dropna(subset=["Region"])

# --- 3. Parse inconsistent dates ---
def parse_date(val):
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return pd.to_datetime(val, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.NaT

df["OrderDate"] = df["OrderDate"].apply(parse_date)

# --- 4. Clean UnitPrice (strip "R", commas, whitespace) ---
def clean_price(val):
    if pd.isna(val):
        return np.nan
    if isinstance(val, (int, float)):
        return float(val)
    cleaned = re.sub(r"[^\d.]", "", str(val))
    return float(cleaned) if cleaned else np.nan

df["UnitPrice"] = df["UnitPrice"].apply(clean_price)

# --- 5. Impute missing numeric values with category-level median ---
df["UnitPrice"] = df.groupby("Product")["UnitPrice"].transform(
    lambda x: x.fillna(x.median())
)
df["Quantity"] = df["Quantity"].fillna(df.groupby("Product")["Quantity"].transform("median"))

# --- 6. Cap extreme outliers in Quantity (data entry errors, e.g. 500 units) ---
q_cap = df["Quantity"].quantile(0.99)
df["Quantity"] = df["Quantity"].clip(upper=q_cap)
df["Quantity"] = df["Quantity"].round().astype(int)

# --- 7. Computed column ---
df["Revenue"] = (df["Quantity"] * df["UnitPrice"]).round(2)

# --- 8. Final tidy-up ---
df = df.sort_values("OrderDate").reset_index(drop=True)

df.to_csv("../data/cleaned_sales_data.csv", index=False)

print(f"Raw rows:      {initial_rows}")
print(f"Cleaned rows:  {len(df)}")
print(f"Rows removed:  {initial_rows - len(df)} (duplicates + unrecoverable missing region)")
print("Saved -> data/cleaned_sales_data.csv")
