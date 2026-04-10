import pandas as pd
import numpy as np

# =========================
# 🧹 CLEAN SALES
# =========================
def clean_sales(sales):

    sales = sales.copy()
    sales.columns = sales.columns.str.strip()

    # remove empty rows
    sales = sales.dropna(how="all")

    # remove internal header rows
    if "Date" in sales.columns:
        drop_keywords = 'المندوب|كود الصنف|تاريخ|كود الفرع'
        sales = sales[~sales["Date"].astype(str).str.contains(drop_keywords, na=False)]

    return sales


# =========================
# 🔢 FIX TYPES
# =========================
def fix_sales_types(sales):

    cols = [
        "Sales Unit Before Edit",
        "Returns Unit Before Edit",
        "Sales Price",
        "Invoice Discounts"
    ]

    for c in cols:
        if c in sales.columns:
            sales[c] = pd.to_numeric(sales[c], errors="coerce").fillna(0)

    return sales


# =========================
# 💰 CALCULATE KPI
# =========================
def calc_sales(sales):

    sales["Total Sales Value"] = sales["Sales Unit Before Edit"] * sales["Sales Price"]
    sales["Returns Value"] = sales["Returns Unit Before Edit"] * sales["Sales Price"]

    sales["Sales After Returns"] = sales["Total Sales Value"] - sales["Returns Value"]

    return sales


# =========================
# 🚀 MAIN PIPELINE
# =========================
def build_sales_pipeline(sales):

    sales = clean_sales(sales)
    sales = fix_sales_types(sales)
    sales = calc_sales(sales)

    # fix rep code
    if "Rep Code" in sales.columns:
        sales["Rep Code"] = pd.to_numeric(sales["Rep Code"], errors="coerce")
        sales = sales.dropna(subset=["Rep Code"])

    # GROUP
    rep_value = sales.groupby("Rep Code", as_index=False)[
        ["Total Sales Value", "Returns Value", "Sales After Returns"]
    ].sum()

    manager_value = sales.groupby("Manager Code", as_index=False)[
        ["Total Sales Value", "Returns Value", "Sales After Returns"]
    ].sum()

    area_value = sales.groupby("Area Code", as_index=False)[
        ["Total Sales Value", "Returns Value", "Sales After Returns"]
    ].sum()

    supervisor_value = sales.groupby("Supervisor Code", as_index=False)[
        ["Total Sales Value", "Returns Value", "Sales After Returns"]
    ].sum()

    return {
        "rep_value": rep_value,
        "manager_value": manager_value,
        "area_value": area_value,
        "supervisor_value": supervisor_value,
        "raw": sales
    }
