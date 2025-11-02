import pandas as pd
from .io_pipeline import fetch_data

def predict_sales_trend():
    df = fetch_data()
    df.columns = df.columns.str.lower()

    # Case 1: dataset has 'quantity'
    if "quantity" in df.columns:
        avg_sales = df["quantity"].mean()
        if avg_sales > 50:
            return "📈 Sales trend is UP (high average quantity sold)."
        else:
            return "📉 Sales trend is DOWN (low average quantity sold)."

    # Case 2: dataset has 'sales'
    elif "sales" in df.columns:
        avg_sales = df["sales"].mean()
        if avg_sales > df["sales"].median():
            return "📈 Sales trend is UP (above median sales)."
        else:
            return "📉 Sales trend is DOWN (below median sales)."

    # Case 3: No usable column
    else:
        return "⚠️ Cannot predict sales trend: dataset missing 'quantity' or 'sales' column."
