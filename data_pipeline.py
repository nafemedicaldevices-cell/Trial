import pandas as pd
import numpy as np


# =========================
# 🧹 CLEAN SALES
# =========================
def clean_sales(df):

    df = df.copy()
    df.columns = df.columns.str.strip()

    # remove empty rows
    df = df.dropna(how="all")

    # remove internal header rows (Arabic noise)
    if "Date" in df.columns:
        df = df[~df["Date"].astype(str).str.contains("المندوب|كود الصنف|تاريخ|كود الفرع", na=False)]

    return df


# =========================
# 🔢 FIX TYPES
# =========================
def fix_types(df):

    num_cols = [
        "Sales Unit Before Edit",
        "Returns Unit Before Edit",
        "Sales Price",
        "Invoice Discounts"
    ]

    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    return df


# =========================
# 💰 CALCULATIONS
# =========================
def calc_kpi(df):

    df["Total Sales Value"] = df["Sales Unit Before Edit"] * df["Sales Price"]
    df["Returns Value"] = df["Returns Unit Before Edit"] * df["Sales Price"]
    df["Sales After Returns"] = df["Total Sales Value"] - df["Returns Value"]

    return df


# =========================
# 🚀 MAIN SALES PIPELINE
# =========================
def build_sales_pipeline(df):

    df = clean_sales(df)
    df = fix_types(df)
    df = calc_kpi(df)

    # fix Rep Code
    if "Rep Code" in df.columns:
        df["Rep Code"] = pd.to_numeric(df["Rep Code"], errors="coerce")
        df = df.dropna(subset=["Rep Code"])

    # GROUP LEVELS
    rep = df.groupby("Rep Code", as_index=False)[
        ["Total Sales Value", "Returns Value", "Sales After Returns", "Invoice Discounts"]
    ].sum()

    manager = df.groupby("Manager Code", as_index=False)[
        ["Total Sales Value", "Returns Value", "Sales After Returns", "Invoice Discounts"]
    ].sum()

    area = df.groupby("Area Code", as_index=False)[
        ["Total Sales Value", "Returns Value", "Sales After Returns", "Invoice Discounts"]
    ].sum()

    supervisor = df.groupby("Supervisor Code", as_index=False)[
        ["Total Sales Value", "Returns Value", "Sales After Returns", "Invoice Discounts"]
    ].sum()

    return {
        "rep_value": rep,
        "manager_value": manager,
        "area_value": area,
        "supervisor_value": supervisor,
        "raw": df
    }
