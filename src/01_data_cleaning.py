"""
01_data_cleaning.py
Clean the UCI Online Retail dataset and export an analysis-ready CSV.

Raw data: ~541K transaction line items from a UK-based online retailer
(Dec 2010 - Dec 2011). Known issues handled here:
  - Cancelled orders (InvoiceNo starting with 'C') and negative quantities
  - Zero/negative unit prices (adjustments, bad debt entries)
  - Missing CustomerID (~25% of rows) -- kept for sales analysis,
    excluded later for customer-level analysis
  - Duplicate line items
  - Non-product stock codes (postage, manual adjustments, etc.)

Usage: python src/01_data_cleaning.py
"""

import pandas as pd

RAW_PATH = "data/online_retail_raw.csv"
CLEAN_PATH = "data/online_retail_clean.csv"

# Stock codes that are not actual products
NON_PRODUCT_CODES = {
    "POST", "D", "DOT", "M", "S", "AMAZONFEE", "m",
    "BANK CHARGES", "PADS", "B", "CRUK", "C2",
}


def load_raw(path: str = RAW_PATH) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["InvoiceDate"])
    print(f"Raw rows: {len(df):,}")
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    n0 = len(df)

    # Standardize types
    df["InvoiceNo"] = df["InvoiceNo"].astype(str)
    df["StockCode"] = df["StockCode"].astype(str).str.strip()
    df["Description"] = df["Description"].astype(str).str.strip()

    # 1. Remove cancellations (credit notes) and negative quantities
    cancels = df["InvoiceNo"].str.startswith("C") | (df["Quantity"] <= 0)
    df = df[~cancels]
    print(f"Removed {cancels.sum():,} cancelled / negative-quantity rows")

    # 2. Remove zero or negative prices (adjustments, samples, bad debt)
    bad_price = df["UnitPrice"] <= 0
    df = df[~bad_price]
    print(f"Removed {bad_price.sum():,} zero/negative price rows")

    # 3. Remove non-product stock codes
    non_product = df["StockCode"].isin(NON_PRODUCT_CODES)
    df = df[~non_product]
    print(f"Removed {non_product.sum():,} non-product rows (postage, fees, etc.)")

    # 4. Drop exact duplicate line items
    dupes = df.duplicated()
    df = df[~dupes]
    print(f"Removed {dupes.sum():,} duplicate rows")

    # 5. Derived columns
    df = df.copy()
    df["Revenue"] = df["Quantity"] * df["UnitPrice"]
    df["InvoiceMonth"] = df["InvoiceDate"].dt.to_period("M").astype(str)

    print(f"Clean rows: {len(df):,} ({len(df) / n0:.1%} of raw retained)")
    print(f"Rows missing CustomerID (kept for sales analysis): "
          f"{df['CustomerID'].isna().sum():,}")
    return df


if __name__ == "__main__":
    df = load_raw()
    df = clean(df)
    df.to_csv(CLEAN_PATH, index=False)
    print(f"Saved -> {CLEAN_PATH}")
