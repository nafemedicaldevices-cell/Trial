import pandas as pd
import numpy as np


# =========================
# 💰 SALES PIPELINE CLEAN
# =========================
def build_sales_pipeline(sales, mapping, codes):

    sales = sales.copy()
    mapping = mapping.copy()
    codes = codes.copy()

    # =========================
    # 🧹 CLEAN COLUMNS
    # =========================
    sales.columns = sales.columns.str.strip()

    expected_cols = [
        'Date','Warehouse Name','Client Code','Client Name','Notes','MF','Mostanad',
        'Rep Code','Sales Unit Before Edit','Returns Unit Before Edit',
        'Sales Price','Invoice Discounts','Sales Value'
    ]

    if len(sales.columns) == len(expected_cols):
        sales.columns = expected_cols

    # =========================
    # 🧼 REMOVE HEADER ROWS INSIDE DATA
    # =========================
    if 'Date' in sales.columns:
        drop_keywords = 'المندوب|كود الفرع|تاريخ|كود الصنف'
        sales = sales[sales['Date'].notna()]
        sales = sales[~sales['Date'].astype(str).str.contains(drop_keywords, na=False)].copy()

    # =========================
    # 🔢 FIX TYPES
    # =========================
    num_cols = [
        'Sales Unit Before Edit',
        'Returns Unit Before Edit',
        'Sales Price',
        'Invoice Discounts'
    ]

    for col in num_cols:
        if col in sales.columns:
            sales[col] = pd.to_numeric(sales[col], errors='coerce').fillna(0)

    sales['Rep Code'] = pd.to_numeric(sales['Rep Code'], errors='coerce')

    # =========================
    # 💰 CALCULATIONS
    # =========================
    sales['Total Sales Value'] = sales['Sales Unit Before Edit'] * sales['Sales Price']
    sales['Returns Value'] = sales['Returns Unit Before Edit'] * sales['Sales Price']
    sales['Sales After Returns'] = sales['Total Sales Value'] - sales['Returns Value']

    # =========================
    # 🧠 GROUP FUNCTION SAFE
    # =========================
    def safe_group(df, group_cols, sum_cols):

        group_cols = [c for c in group_cols if c in df.columns]
        sum_cols = [c for c in sum_cols if c in df.columns]

        if not group_cols:
            return pd.DataFrame(columns=sum_cols)

        return df.groupby(group_cols, as_index=False)[sum_cols].sum()

    # =========================
    # 📊 GROUPS
    # =========================
    results = {}

    GROUP_DEFS = {
        "rep_value": {
            "group": ['Rep Code'],
            "sum": ['Total Sales Value','Returns Value','Sales After Returns','Invoice Discounts']
        },
        "manager_value": {
            "group": ['Manager Code'],
            "sum": ['Total Sales Value','Returns Value','Sales After Returns','Invoice Discounts']
        },
        "area_value": {
            "group": ['Area Code'],
            "sum": ['Total Sales Value','Returns Value','Sales After Returns','Invoice Discounts']
        },
        "supervisor_value": {
            "group": ['Supervisor Code'],
            "sum": ['Total Sales Value','Returns Value','Sales After Returns','Invoice Discounts']
        },
        "rep_products": {
            "group": ['Rep Code','Product Code','Product Name'],
            "sum": ['Sales Value','Sales After Returns']
        }
    }

    for name, cfg in GROUP_DEFS.items():
        results[name] = safe_group(sales, cfg["group"], cfg["sum"])

    # =========================
    # 🧾 OUTPUT
    # =========================
    return results
