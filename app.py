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
# 📂 LOAD DATA
# =========================
def load_data():
    return {
        "sales": pd.read_excel("Sales.xlsx"),
        "overdue": pd.read_excel("Overdue.xlsx"),
        "opening": pd.read_excel("Opening.xlsx"),

        "target_rep": pd.read_excel("Target Rep.xlsx"),
        "target_manager": pd.read_excel("Target Manager.xlsx"),
        "target_area": pd.read_excel("Target Area.xlsx"),
        "target_supervisor": pd.read_excel("Target Supervisor.xlsx"),
        "target_evak": pd.read_excel("Target Evak.xlsx"),

        "mapping": pd.read_excel("Mapping.xlsx"),
        "codes": pd.read_excel("Code.xlsx")
    }


# =========================
# 🚀 TARGET PIPELINE (FIXED PRODUCTS)
# =========================
def build_target_pipeline(df, id_name, mapping):

    df = df.copy()
    mapping = mapping.copy()

    df.columns = df.columns.str.strip()

    fixed_cols = [c for c in ["Year", "Product Code", "Old Product Name", "Sales Price"] if c in df.columns]
    dynamic_cols = [c for c in df.columns if c not in fixed_cols]

    df = df.melt(
        id_vars=fixed_cols,
        value_vars=dynamic_cols,
        var_name=id_name,
        value_name="Target (Unit)"
    )

    df[id_name] = pd.to_numeric(
        df[id_name].astype(str).str.replace(r"[^0-9]", "", regex=True),
        errors="coerce"
    )

    df["Product Code"] = pd.to_numeric(df["Product Code"], errors="coerce")
    mapping["Product Code"] = pd.to_numeric(mapping["Product Code"], errors="coerce")

    mapping = mapping.drop_duplicates("Product Code")

    df = df.merge(mapping, on="Product Code", how="left")

    df["Target (Unit)"] = pd.to_numeric(df["Target (Unit)"], errors="coerce").fillna(0)
    df["Sales Price"] = pd.to_numeric(df["Sales Price"], errors="coerce").fillna(0)

    df["Full Value"] = df["Target (Unit)"] * df["Sales Price"]

    full = df.copy()
    full["Value"] = full["Full Value"]

    month = df.copy()
    month["Value"] = full["Full Value"] * (current_month / 12)

    quarter = df.copy()
    quarter["Value"] = full["Full Value"] * (past_quarters / 4)

    ytd = df.copy()
    ytd["Value"] = full["Full Value"] * (current_month / 12)

    # =========================
    # 📊 SAFE GROUP
    # =========================
    def group(d):
        return d.groupby([id_name], as_index=False)["Value"].sum()

    value_table = group(full).rename(columns={"Value": "Full Year 🏆"})
    value_table["Month 📅"] = group(month)["Value"]
    value_table["Quarter 📊"] = group(quarter)["Value"]
    value_table["YTD 📈"] = group(ytd)["Value"]

    # =========================
    # 📦 PRODUCTS (FIXED SAFETY)
    # =========================
    def product_group(d):

        needed_cols = [id_name, "Product Code", "Product Name", "Target (Unit)", "Value"]
        needed_cols = [c for c in needed_cols if c in d.columns]

        return (
            d[needed_cols]
            .groupby([id_name, "Product Code", "Product Name"], as_index=False)
            .agg(
                Units=("Target (Unit)", "sum"),
                Value=("Value", "sum")
            )
        )

    return {
        "value_table": value_table,
        "products_full": product_group(full),
        "products_month": product_group(month),
        "products_quarter": product_group(quarter),
        "products_ytd": product_group(ytd),
    }


# =========================
# 💰 SALES PIPELINE (SAFE VERSION)
# =========================
def build_sales_pipeline(sales, mapping, codes):

    sales = sales.copy()
    sales.columns = sales.columns.str.strip()

    # numeric safety
    for col in sales.columns:
        if sales[col].dtype == "object":
            continue
        sales[col] = pd.to_numeric(sales[col], errors="ignore")

    # IDs
    if "Rep Code" in sales.columns:
        sales["Rep Code"] = pd.to_numeric(sales["Rep Code"], errors="coerce").astype("Int64")

    if "Old Product Code" in sales.columns:
        sales["Old Product Code"] = pd.to_numeric(sales["Old Product Code"], errors="coerce").astype("Int64")

    # mapping
    if "Old Product Code" in sales.columns:
        mapping["Product Code"] = pd.to_numeric(mapping["Product Code"], errors="coerce")
        sales["Old Product Code"] = sales["Old Product Code"].astype("float")

        sales = sales.merge(mapping, left_on="Old Product Code", right_on="Product Code", how="left")

    # codes
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce").astype("Int64")
    sales = sales.merge(codes, on="Rep Code", how="left")

    # calculations
    for col in ["Sales Unit Before Edit", "Returns Unit Before Edit", "Sales Price"]:
        if col in sales.columns:
            sales[col] = pd.to_numeric(sales[col], errors="coerce").fillna(0)

    sales["Total Sales Value"] = sales.get("Sales Unit Before Edit", 0) * sales.get("Sales Price", 0)
    sales["Returns Value"] = sales.get("Returns Unit Before Edit", 0) * sales.get("Sales Price", 0)
    sales["Net Sales"] = sales["Total Sales Value"] - sales["Returns Value"]

    def safe_group(df, group_cols, sum_cols):
        group_cols = [c for c in group_cols if c in df.columns]
        sum_cols = [c for c in sum_cols if c in df.columns]

        if not group_cols:
            return pd.DataFrame()

        return df.groupby(group_cols, as_index=False)[sum_cols].sum()

    return {
        "rep": safe_group(sales, ["Rep Code"], ["Net Sales"]),
        "manager": safe_group(sales, ["Manager Code"], ["Net Sales"]),
        "area": safe_group(sales, ["Area Code"], ["Net Sales"]),
        "supervisor": safe_group(sales, ["Supervisor Code"], ["Net Sales"]),
        "products": safe_group(sales, ["Rep Code", "Product Code", "Product Name"], ["Net Sales"]),
    }


# =========================
# 🎨 STREAMLIT UI
# =========================
st.set_page_config(layout="wide")
st.title("📊 Unified KPI Dashboard (TARGET + SALES)")

data = load_data()

# =========================
# TARGET
# =========================
st.header("🎯 TARGET KPI")

rep_t = build_target_pipeline(data["target_rep"], "Rep Code", data["mapping"])
manager_t = build_target_pipeline(data["target_manager"], "Manager Code", data["mapping"])
area_t = build_target_pipeline(data["target_area"], "Area Code", data["mapping"])

st.subheader("Rep Target")
st.dataframe(rep_t["value_table"])

st.subheader("Manager Target")
st.dataframe(manager_t["value_table"])

st.subheader("Area Target")
st.dataframe(area_t["value_table"])


# =========================
# SALES
# =========================
st.header("💰 SALES KPI")

sales = build_sales_pipeline(data["sales"], data["mapping"], data["codes"])

st.subheader("Rep Sales")
st.dataframe(sales["rep"])

st.subheader("Manager Sales")
st.dataframe(sales["manager"])

st.subheader("Area Sales")
st.dataframe(sales["area"])

st.subheader("Products Sales")
st.dataframe(sales["products"])
