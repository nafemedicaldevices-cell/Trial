import pandas as pd
import numpy as np


# =========================
# 🧼 CLEAN COLUMNS (IMPORTANT)
# =========================
def clean_columns(df):
    df = df.copy()
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    return df


# =========================
# 📥 LOAD DATA
# =========================
def load_data():
    return {
        "sales": pd.read_excel("Sales.xlsx"),

        "target_rep": pd.read_excel("Target Rep.xlsx"),
        "target_manager": pd.read_excel("Target Manager.xlsx"),
        "target_area": pd.read_excel("Target Area.xlsx"),
        "target_supervisor": pd.read_excel("Target Supervisor.xlsx"),

        "mapping": pd.read_excel("Mapping.xlsx"),
        "codes": pd.read_excel("Code.xlsx")
    }


# =========================
# 💰 SALES PIPELINE
# =========================
def build_sales_pipeline(sales, mapping, codes):

    sales = clean_columns(sales)
    mapping = clean_columns(mapping)
    codes = clean_columns(codes)

    # =========================
    # 🔢 NUMERIC CLEAN
    # =========================
    num_cols = [
        "sales_unit_before_edit",
        "returns_unit_before_edit",
        "sales_price",
        "invoice_discounts"
    ]

    for c in num_cols:
        if c in sales.columns:
            sales[c] = pd.to_numeric(sales[c], errors="coerce").fillna(0)
        else:
            sales[c] = 0


    # =========================
    # 💰 CALCULATIONS
    # =========================
    sales["total_sales_value"] = sales["sales_unit_before_edit"] * sales["sales_price"]
    sales["returns_value"] = sales["returns_unit_before_edit"] * sales["sales_price"]
    sales["sales_after_returns"] = sales["total_sales_value"] - sales["returns_value"]


    # =========================
    # 🔑 SAFE CODE
    # =========================
    if "rep_code" not in sales.columns:
        sales["rep_code"] = np.nan

    sales["rep_code"] = sales["rep_code"].astype(str)

    if "rep_code" in codes.columns:
        codes["rep_code"] = codes["rep_code"].astype(str)
        sales = sales.merge(codes, on="rep_code", how="left")


    # =========================
    # 🧠 MAPPING SAFE
    # =========================
    if "old_product_code" in sales.columns and "old_product_code" in mapping.columns:
        sales["old_product_code"] = pd.to_numeric(sales["old_product_code"], errors="coerce")
        sales = sales.merge(mapping, on="old_product_code", how="left")

    return sales


# =========================
# 🎯 TARGET PIPELINE
# =========================
def build_target_pipeline(df, key_col):

    df = clean_columns(df)

    key_col = key_col.lower().replace(" ", "_")

    if key_col in df.columns:
        df[key_col] = df[key_col].astype(str)

    for c in df.columns:
        if "target" in c:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    return df
