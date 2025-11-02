import pandas as pd
import matplotlib.pyplot as plt
from .io_pipeline import fetch_data

def sales_summary():
    df = fetch_data()
    df.columns = df.columns.str.lower()

    # Handle different possible column sets
    if {"quantity", "price"}.issubset(df.columns):
        summary = df.groupby("region")[["quantity", "price"]].sum()
    elif {"sales"}.issubset(df.columns):
        summary = df.groupby("region", as_index=False)["sales"].sum()
        summary.rename(columns={"sales": "total_sales"}, inplace=True)
    else:
        summary = pd.DataFrame({"error": ["Expected columns not found in dataset"]})

    return summary


def visualize_sales():
    df = fetch_data()
    df.columns = df.columns.str.lower()

    if {"region", "sales"}.issubset(df.columns):
        sales_by_region = df.groupby("region")["sales"].sum()
        sales_by_region.plot(kind="bar", title="Sales by Region")
        plt.xlabel("Region")
        plt.ylabel("Total Sales")
        plt.tight_layout()
        plt.show()
    elif {"region", "quantity"}.issubset(df.columns):
        sales_by_region = df.groupby("region")["quantity"].sum()
        sales_by_region.plot(kind="bar", title="Quantity Sold by Region")
        plt.xlabel("Region")
        plt.ylabel("Total Quantity")
        plt.tight_layout()
        plt.show()
    else:
        print("❌ Cannot visualize: missing 'region' and 'sales'/'quantity' columns.")
