import pandas as pd
import numpy as np
import streamlit as st

# =========================
# 📅 TIME SETTINGS
# =========================
current_month = pd.Timestamp.today().month
current_quarter = (current_month - 1) // 3 + 1
past_quarters = max(current_quarter - 1, 0)

# =========================
# 🧼 CLEAN COLUMNS FUNCTION (IMPORTANT)
# =========================
def clean_columns(df):
    df = df.copy()
    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.replace(" ", "")
    return df

# =========================
# 📂 LOAD DATA
# =========================
def load_data():
    return {
        "target_rep": pd.read_excel("Target Rep.xlsx"),
        "target_manager": pd.read_excel("Target Manager.xlsx"),
        "target_area": pd.read_excel("Target Area.xlsx"),
        "target_supervisor": pd.read_excel("Target Supervisor.xlsx"),
        "target_evak": pd.read_excel("Target Evak.xlsx"),

        "sales": pd.read_excel("Sales.xlsx"),

        "mapping": pd.read_excel("Mapping.xlsx"),
        "codes": pd.read_excel("Code.xlsx"),
    }

# =========================
# 🎯 TARGET PIPELINE
# =========================
def build_target_pipeline(df, id_name, mapping):

    df = df.copy()
    mapping = mapping.copy()

    df = clean_columns(df)
    mapping = clean_columns(mapping)

    fixed_cols = [c for c in ["Year", "ProductCode", "OldProductName", "SalesPrice"] if c in df.columns]
    dynamic_cols = [c for c in df.columns if c not in fixed_cols]

    df = df.melt(
        id_vars=fixed_cols,
        value_vars=dynamic_cols,
        var_name=id_name,
        value_name="TargetUnit"
    )

    df[id_name] = pd.to_numeric(df[id_name].astype(str).str.replace(r"[^0-9]", "", regex=True), errors="coerce")
    df["ProductCode"] = pd.to_numeric(df["ProductCode"], errors="coerce")

    mapping["ProductCode"] = pd.to_numeric(mapping["ProductCode"], errors="coerce")
    mapping = mapping.drop_duplicates("ProductCode")

    df = df.merge(mapping, on="ProductCode", how="left")

    df["TargetUnit"] = pd.to_numeric(df["TargetUnit"], errors="coerce").fillna(0)
    df["SalesPrice"] = pd.to_numeric(df["SalesPrice"], errors="coerce").fillna(0)

    df["FullValue"] = df["TargetUnit"] * df["SalesPrice"]

    full = df.copy()
    full["Value"] = full["FullValue"]

    def group(d):
        return d.groupby([id_name], as_index=False)["Value"].sum()

    value_table = group(full).rename(columns={"Value": "FullYear"})
    value_table["Month"] = full["FullValue"] * (current_month / 12)
    value_table["Quarter"] = full["FullValue"] * (past_quarters / 4)
    value_table["YTD"] = full["FullValue"] * (current_month / 12)

    return {"value_table": value_table}

# =========================
# 💰 SALES PIPELINE
# =========================
def build_sales_pipeline(sales, mapping, codes):

    sales = sales.copy()
    mapping = mapping.copy()
    codes = codes.copy()

    # =========================
    # CLEAN ALL COLUMNS FIRST
    # =========================
    sales = clean_columns(sales)
    mapping = clean_columns(mapping)
    codes = clean_columns(codes)

    # =========================
    # SAFE COLUMN CREATION
    # =========================
    for col in [
        "RepCode","ManagerCode","AreaCode","SupervisorCode",
        "OldProductCode","OldProductName"
    ]:
        if col not in sales.columns:
            sales[col] = np.nan

    # =========================
    # PRODUCT HEADER LOGIC
    # =========================
    if "Date" in sales.columns:

        mask = sales["Date"].astype(str).str.strip().eq("كودالصنف")

        if "ClientCode" in sales.columns:
            sales.loc[mask, "OldProductCode"] = sales.loc[mask, "ClientCode"]

        if "ClientName" in sales.columns:
            sales.loc[mask, "OldProductName"] = sales.loc[mask, "ClientName"]

        sales["OldProductCode"] = sales["OldProductCode"].ffill()
        sales["OldProductName"] = sales["OldProductName"].ffill()

        drop_keywords = "المندوب|كودالفرع|تاريخ|كودالصنف"

        sales = sales[
            sales["Date"].notna() &
            ~sales["Date"].astype(str).str.contains(drop_keywords, na=False)
        ].copy()

    # =========================
    # NUMERIC CLEAN
    # =========================
    num_cols = [
        "SalesUnitBeforeEdit",
        "ReturnsUnitBeforeEdit",
        "SalesPrice",
        "InvoiceDiscounts",
        "SalesValue"
    ]

    for col in num_cols:
        if col in sales.columns:
            sales[col] = pd.to_numeric(sales[col], errors="coerce").fillna(0)

    # =========================
    # IDS SAFE
    # =========================
    sales["RepCode"] = pd.to_numeric(sales["RepCode"], errors="coerce").astype("Int64")

    if "RepCode" in codes.columns:
        codes["RepCode"] = pd.to_numeric(codes["RepCode"], errors="coerce").astype("Int64")
        codes = codes.drop_duplicates("RepCode")
        sales = sales.merge(codes, on="RepCode", how="left", validate="m:1")

    # =========================
    # NEXT FACTOR
    # =========================
    if "NextFactor" not in sales.columns:
        sales["NextFactor"] = 1

    sales["NextFactor"] = pd.to_numeric(sales["NextFactor"], errors="coerce").fillna(1)

    # =========================
    # CALCULATIONS
    # =========================
    sales["TotalSalesValue"] = sales["SalesUnitBeforeEdit"] * sales["SalesPrice"]
    sales["ReturnsValue"] = sales["ReturnsUnitBeforeEdit"] * sales["SalesPrice"]

    sales["SalesAfterReturns"] = sales["TotalSalesValue"] - sales["ReturnsValue"]

    sales["NetSalesUnit"] = (
        (sales["SalesUnitBeforeEdit"] - sales["ReturnsUnitBeforeEdit"])
        * sales["NextFactor"]
    )

    # =========================
    # SAFE GROUP ENGINE
    # =========================
    def safe_group(df, group_cols, sum_cols):

        group_cols = [c for c in group_cols if c in df.columns]
        sum_cols = [c for c in sum_cols if c in df.columns]

        if not group_cols or not sum_cols:
            return pd.DataFrame()

        return df.groupby(group_cols, as_index=False)[sum_cols].sum()

    return {
        "rep_value": safe_group(sales, ["RepCode"], ["TotalSalesValue","ReturnsValue","SalesAfterReturns"]),
        "manager_value": safe_group(sales, ["ManagerCode"], ["TotalSalesValue","ReturnsValue","SalesAfterReturns"]),
        "area_value": safe_group(sales, ["AreaCode"], ["TotalSalesValue","ReturnsValue","SalesAfterReturns"]),
        "supervisor_value": safe_group(sales, ["SupervisorCode"], ["TotalSalesValue","ReturnsValue","SalesAfterReturns"]),

        "rep_products": safe_group(sales, ["RepCode","OldProductCode","OldProductName"], ["SalesAfterReturns","NetSalesUnit"])
    }

# =========================
# 🚀 STREAMLIT UI
# =========================
st.set_page_config(layout="wide")
st.title("📊 Unified KPI System (FINAL FIXED)")

data = load_data()

# TARGET
rep = build_target_pipeline(data["target_rep"], "RepCode", data["mapping"])
manager = build_target_pipeline(data["target_manager"], "ManagerCode", data["mapping"])
area = build_target_pipeline(data["target_area"], "AreaCode", data["mapping"])
supervisor = build_target_pipeline(data["target_supervisor"], "SupervisorCode", data["mapping"])
evak = build_target_pipeline(data["target_evak"], "EvakCode", data["mapping"])

# SALES
sales = build_sales_pipeline(data["sales"], data["mapping"], data["codes"])

# =========================
# TARGET UI
# =========================
st.header("🎯 TARGET KPI")
st.dataframe(rep["value_table"])
st.dataframe(manager["value_table"])
st.dataframe(area["value_table"])
st.dataframe(supervisor["value_table"])
st.dataframe(evak["value_table"])

# =========================
# SALES UI
# =========================
st.header("💰 SALES KPI")
st.dataframe(sales["rep_value"])
st.dataframe(sales["manager_value"])
st.dataframe(sales["area_value"])
st.dataframe(sales["supervisor_value"])
