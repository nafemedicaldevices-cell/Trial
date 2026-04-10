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
        "target_evak": pd.read_excel("Target Evak.xlsx"),
        "mapping": pd.read_excel("Mapping.xlsx"),
        "codes": pd.read_excel("Code.xlsx")
    }


# =========================
# 🔍 SMART COLUMN FINDER
# =========================
def find_col(df, keywords):
    for c in df.columns:
        if any(k.lower() in c.lower() for k in keywords):
            return c
    return None


# =========================
# 💰 SALES PIPELINE (FIXED)
# =========================
def build_sales(df):

    df = df.copy()

    # clean columns
    df.columns = df.columns.str.strip()

    # detect columns dynamically
    qty_col = find_col(df, ["sales unit", "unit", "qty"])
    return_col = find_col(df, ["return"])
    price_col = find_col(df, ["price"])

    if qty_col is None or price_col is None:
        raise ValueError(f"Missing required columns. Found: {df.columns}")

    # numeric conversion
    df[qty_col] = pd.to_numeric(df[qty_col], errors="coerce").fillna(0)
    df[price_col] = pd.to_numeric(df[price_col], errors="coerce").fillna(0)

    if return_col:
        df[return_col] = pd.to_numeric(df[return_col], errors="coerce").fillna(0)
    else:
        df["Returns Unit Before Edit"] = 0
        return_col = "Returns Unit Before Edit"

    # KPI
    df["Total Sales Value"] = df[qty_col] * df[price_col]
    df["Returns Value"] = df[return_col] * df[price_col]
    df["Sales After Returns"] = df["Total Sales Value"] - df["Returns Value"]

    return df


# =========================
# 📊 SALES GROUPING
# =========================
def build_sales_pipeline(df):

    df = build_sales(df)

    # Rep
    rep = df.groupby("Rep Code", as_index=False)[
        ["Total Sales Value", "Returns Value", "Sales After Returns"]
    ].sum()

    # Manager (if exists)
    manager = df.groupby("Manager Code", as_index=False)[
        ["Total Sales Value", "Returns Value", "Sales After Returns"]
    ].sum() if "Manager Code" in df.columns else pd.DataFrame()

    # Area
    area = df.groupby("Area Code", as_index=False)[
        ["Total Sales Value", "Returns Value", "Sales After Returns"]
    ].sum() if "Area Code" in df.columns else pd.DataFrame()

    # Supervisor
    supervisor = df.groupby("Supervisor Code", as_index=False)[
        ["Total Sales Value", "Returns Value", "Sales After Returns"]
    ].sum() if "Supervisor Code" in df.columns else pd.DataFrame()

    return {
        "rep_value": rep,
        "manager_value": manager,
        "area_value": area,
        "supervisor_value": supervisor,
        "raw": df
    }


# =========================
# 🎯 TARGET PIPELINE (SIMPLE)
# =========================
def build_target(df, id_name, mapping):

    df = df.copy()
    mapping = mapping.copy()

    df.columns = df.columns.str.strip()

    fixed_cols = [c for c in ["Year", "Product Code", "Sales Price"] if c in df.columns]
    dynamic_cols = [c for c in df.columns if c not in fixed_cols]

    df = df.melt(
        id_vars=fixed_cols,
        value_vars=dynamic_cols,
        var_name=id_name,
        value_name="Target Units"
    )

    df[id_name] = pd.to_numeric(df[id_name].astype(str).str.replace(r"[^0-9]", "", regex=True), errors="coerce")
    df["Product Code"] = pd.to_numeric(df["Product Code"], errors="coerce")

    mapping["Product Code"] = pd.to_numeric(mapping["Product Code"], errors="coerce")
    mapping = mapping.drop_duplicates("Product Code")

    df = df.merge(mapping, on="Product Code", how="left")

    df["Target Units"] = pd.to_numeric(df["Target Units"], errors="coerce").fillna(0)
    df["Sales Price"] = pd.to_numeric(df["Sales Price"], errors="coerce").fillna(0)

    df["Target Value"] = df["Target Units"] * df["Sales Price"]

    return df.groupby([id_name], as_index=False)["Target Value"].sum()
