import pandas as pd
import numpy as np
import os

# =========================
# 📂 SALES CLEANING
# =========================
def load_sales():

    sales = pd.read_excel("Sales.xlsx")
    sales.columns = sales.columns.str.strip()

    # =========================
    # 🔥 FIND REP CODE COLUMN
    # =========================
    rep_candidates = [
        "Rep Code", "RepCode", "Rep_Code",
        "Sales Rep Code", "مندوب"
    ]

    rep_col = None
    for c in rep_candidates:
        if c in sales.columns:
            rep_col = c
            break

    if rep_col is None:
        raise Exception(f"❌ Rep Code not found: {sales.columns.tolist()}")

    sales["Rep Code"] = sales[rep_col].astype(str).str.strip()

    # =========================
    # NUMERIC CLEANING
    # =========================
    num_cols = ["Sales Value", "Returns Value", "Invoice Discounts"]

    for col in num_cols:
        if col not in sales.columns:
            sales[col] = 0
        else:
            sales[col] = pd.to_numeric(sales[col], errors="coerce").fillna(0)

    # =========================
    # 💰 NET SALES
    # =========================
    sales["Net Sales"] = (
        sales["Sales Value"]
        - sales["Returns Value"]
        - sales["Invoice Discounts"]
    )

    return sales


# =========================
# 📂 TARGETS
# =========================
def load_targets():

    df = pd.read_excel("Target Rep.xlsx", sheet_name=None)

    all_data = []

    for _, sheet in df.items():

        sheet.columns = sheet.columns.str.strip()

        fixed_cols = ["Year", "Product Code", "Old Product Name", "Sales Price"]

        sheet = sheet.melt(
            id_vars=fixed_cols,
            var_name="Code",
            value_name="Target (Year)"
        )

        sheet["Target (Year)"] = pd.to_numeric(sheet["Target (Year)"], errors="coerce")

        sheet["Target (Unit)"] = sheet["Target (Year)"] / 12
        sheet["Target (Value)"] = sheet["Target (Unit)"] * sheet["Sales Price"]

        months = [
            "Jan","Feb","Mar","Apr","May","Jun",
            "Jul","Aug","Sep","Oct","Nov","Dec"
        ]

        df_long = sheet.loc[sheet.index.repeat(12)].copy()
        df_long["Month"] = months * len(sheet)

        df_long["Target (Value)"] = sheet["Target (Value)"].repeat(12).values

        all_data.append(df_long)

    return pd.concat(all_data, ignore_index=True)
