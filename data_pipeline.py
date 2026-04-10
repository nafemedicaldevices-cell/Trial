import pandas as pd
import numpy as np


# =========================
# 📂 LOAD DATA
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
# 🧹 CLEAN SALES (IMPORTANT STEP 1)
# =========================
def clean_sales(df):

    df = df.copy()
    df.columns = df.columns.str.strip()

    # 👇 هنا هنسمّي الأعمدة يدوي (لأنك لسه بتظبطي الداتا)
    expected_cols = [
        "Date",
        "Warehouse Name",
        "Client Code",
        "Client Name",
        "Rep Code",
        "Sales Unit",
        "Returns Unit",
        "Price",
        "Discount",
        "Sales Value"
    ]

    if len(df.columns) == len(expected_cols):
        df.columns = expected_cols

    return df


# =========================
# 💰 KPI CALCULATION
# =========================
def build_sales_pipeline(df):

    df = clean_sales(df)

    # numeric
    for c in ["Sales Unit", "Returns Unit", "Price", "Discount"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    # calculations
    df["Total Sales Value"] = df["Sales Unit"] * df["Price"]
    df["Returns Value"] = df["Returns Unit"] * df["Price"]
    df["Sales After Returns"] = df["Total Sales Value"] - df["Returns Value"]

    # groups safe
    def grp(col):
        if col not in df.columns:
            return pd.DataFrame()
        return df.groupby(col, as_index=False)[
            ["Total Sales Value", "Returns Value", "Sales After Returns"]
        ].sum()

    return {
        "rep_value": grp("Rep Code"),
        "manager_value": grp("Manager Code"),
        "area_value": grp("Area Code"),
        "supervisor_value": grp("Supervisor Code"),
        "raw": df
    }

    return {
        "rep_value": grp("Rep Code"),
        "manager_value": grp("Manager Code"),
        "area_value": grp("Area Code"),
        "supervisor_value": grp("Supervisor Code"),
        "raw": df
    }
