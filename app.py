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
        "target_rep": pd.read_excel("Target Rep.xlsx"),
        "target_manager": pd.read_excel("Target Manager.xlsx"),
        "target_area": pd.read_excel("Target Area.xlsx"),
        "target_supervisor": pd.read_excel("Target Supervisor.xlsx"),
        "target_evak": pd.read_excel("Target Evak.xlsx"),
        "mapping": pd.read_excel("Mapping.xlsx"),
    }

# =========================
# 🚀 TARGET PIPELINE
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

    df["Value"] = df["Target (Unit)"] * df["Sales Price"]

    full = df.copy()
    month = df.copy()
    quarter = df.copy()
    ytd = df.copy()

    # =========================
    # 📊 VALUE GROUP
    # =========================
    def group(d):
        return d.groupby([id_name], as_index=False)["Value"].sum()

    value_table = group(full).rename(columns={"Value": "Full Year 🏆"})
    value_table["Month 📅"] = group(month)["Value"]
    value_table["Quarter 📊"] = group(quarter)["Value"]
    value_table["YTD 📈"] = group(ytd)["Value"]

    # =========================
    # 📦 PRODUCTS GROUP (FIXED)
    # =========================
    def product_group(d):

        if "Product Name" not in d.columns:
            d["Product Name"] = "UNKNOWN"

        return (
            d.groupby(
                [id_name, "Product Code", "Product Name"],
                as_index=False
            )
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
# 🎨 STREAMLIT UI
# =========================
st.set_page_config(layout="wide")
st.title("📊 TARGET DASHBOARD")

data = load_data()

rep = build_target_pipeline(data["target_rep"], "Rep Code", data["mapping"])
manager = build_target_pipeline(data["target_manager"], "Manager Code", data["mapping"])
area = build_target_pipeline(data["target_area"], "Area Code", data["mapping"])
supervisor = build_target_pipeline(data["target_supervisor"], "Supervisor Code", data["mapping"])
evak = build_target_pipeline(data["target_evak"], "Evak Code", data["mapping"])

# =========================
# 📊 VALUE KPI
# =========================
st.header("📊 VALUE KPI")

st.subheader("Rep")
st.dataframe(rep["value_table"])

st.subheader("Manager")
st.dataframe(manager["value_table"])

st.subheader("Area")
st.dataframe(area["value_table"])

st.subheader("Supervisor")
st.dataframe(supervisor["value_table"])

st.subheader("Evak")
st.dataframe(evak["value_table"])

# =========================
# 📦 PRODUCTS KPI
# =========================
st.header("📦 PRODUCTS KPI")

st.subheader("Rep Products")
st.dataframe(rep["products_full"])

st.subheader("Manager Products")
st.dataframe(manager["products_full"])

st.subheader("Area Products")
st.dataframe(area["products_full"])

st.subheader("Supervisor Products")
st.dataframe(supervisor["products_full"])

st.subheader("Evak Products")
st.dataframe(evak["products_full"])
