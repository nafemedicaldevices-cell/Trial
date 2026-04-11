import streamlit as st
import pandas as pd
import numpy as np

# =========================
# 🎨 PAGE SETUP
# =========================
st.set_page_config(layout="wide")
st.title("📊 Unified KPI Dashboard")


# =========================
# 📥 LOAD DATA (ONE PLACE)
# =========================
@st.cache_data
def load_data():
    return {
        "sales": pd.read_excel("Sales.xlsx"),
        "overdue": pd.read_excel("Overdue.xlsx"),
        "opening": pd.read_excel("Opening.xlsx"),
        "mapping": pd.read_excel("Mapping.xlsx"),
        "codes": pd.read_excel("Code.xlsx"),

        "target_rep": pd.read_excel("Target Rep.xlsx"),
        "target_manager": pd.read_excel("Target Manager.xlsx"),
        "target_area": pd.read_excel("Target Area.xlsx"),
        "target_supervisor": pd.read_excel("Target Supervisor.xlsx"),
        "target_evak": pd.read_excel("Target Evak.xlsx"),
    }


data = load_data()


# =========================
# 🧠 COMMON UTILITIES
# =========================
def to_numeric(df, cols):
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    return df


def merge_codes(df, codes):
    codes = codes.copy()
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce").astype("Int64")
    df["Rep Code"] = pd.to_numeric(df["Rep Code"], errors="coerce").astype("Int64")
    return df.merge(codes, on="Rep Code", how="left")


# =========================
# 🚀 SALES PIPELINE
# =========================
def sales_pipeline(sales, mapping, codes):

    sales = sales.copy()
    sales.columns = sales.columns.str.strip()

    sales = to_numeric(sales, [
        'Sales Unit Before Edit',
        'Returns Unit Before Edit',
        'Sales Price',
        'Invoice Discounts',
        'Sales Value'
    ])

    sales = merge_codes(sales, codes)

    sales["Total Sales Value"] = sales["Sales Unit Before Edit"] * sales["Sales Price"]
    sales["Returns Value"] = sales["Returns Unit Before Edit"] * sales["Sales Price"]
    sales["Net Sales"] = sales["Total Sales Value"] - sales["Returns Value"]

    return {
        "rep": sales.groupby("Rep Code")[["Total Sales Value","Returns Value","Net Sales"]].sum().reset_index(),
        "manager": sales.groupby("Manager Code")[["Total Sales Value","Returns Value","Net Sales"]].sum().reset_index(),
        "area": sales.groupby("Area Code")[["Total Sales Value","Returns Value","Net Sales"]].sum().reset_index(),
    }


# =========================
# 📦 OVERDUE PIPELINE
# =========================
def overdue_pipeline(overdue, codes):

    df = overdue.copy()
    df = df.iloc[:, :9]

    df.columns = [
        "Client Name","Client Code","15","30","60","90","120","120+","Balance"
    ]

    df = to_numeric(df, ["120","120+","Balance"])
    df["Overdue"] = df["120"] + df["120+"]

    df = merge_codes(df, codes)

    return {
        "rep": df.groupby("Rep Code")["Overdue"].sum().reset_index(),
        "manager": df.groupby("Manager Code")["Overdue"].sum().reset_index(),
        "area": df.groupby("Area Code")["Overdue"].sum().reset_index(),
    }


# =========================
# 📦 OPENING PIPELINE
# =========================
def opening_pipeline(opening, codes):

    df = opening.copy()

    df.columns = [
        'Branch',"Evak",'Opening Balance','Sales After Invoice Discounts',
        'Returns','Sales Before Extra Discounts','Cash Collection',
        'Collection Checks','Returned Chick','Collection Returned Chick',
        "Extra Discounts",'Daienah','End Balance'
    ]

    df = to_numeric(df, [
        'Opening Balance','Sales After Invoice Discounts','Returns',
        'Cash Collection','Collection Checks','End Balance'
    ])

    df["Total Collection"] = df["Cash Collection"] + df["Collection Checks"]

    df = merge_codes(df, codes)

    return {
        "rep": df.groupby("Rep Code")[["Opening Balance","Total Collection","End Balance"]].sum().reset_index(),
        "manager": df.groupby("Manager Code")[["Opening Balance","Total Collection","End Balance"]].sum().reset_index(),
        "area": df.groupby("Area Code")[["Opening Balance","Total Collection","End Balance"]].sum().reset_index(),
    }


# =========================
# 🚀 TARGET PIPELINE (GENERIC)
# =========================
def target_pipeline(df, id_col, mapping):

    df = df.copy()
    df.columns = df.columns.str.strip()

    fixed = [c for c in ["Year","Product Code","Product Name","Sales Price"] if c in df.columns]
    dyn = [c for c in df.columns if c not in fixed]

    df = df.melt(id_vars=fixed, value_vars=dyn,
                 var_name=id_col, value_name="Target")

    df[id_col] = pd.to_numeric(df[id_col], errors="coerce")

    df["Product Code"] = pd.to_numeric(df["Product Code"], errors="coerce")
    mapping["Product Code"] = pd.to_numeric(mapping["Product Code"], errors="coerce")

    df = df.merge(mapping, on="Product Code", how="left")

    df["Target"] = pd.to_numeric(df["Target"], errors="coerce").fillna(0)
    df["Sales Price"] = pd.to_numeric(df["Sales Price"], errors="coerce").fillna(0)

    df["Value"] = df["Target"] * df["Sales Price"]

    return df.groupby(id_col)["Value"].sum().reset_index()


# =========================
# 🚀 RUN ALL PIPELINES
# =========================
sales = sales_pipeline(data["sales"], data["mapping"], data["codes"])
overdue = overdue_pipeline(data["overdue"], data["codes"])
opening = opening_pipeline(data["opening"], data["codes"])

targets = {
    "rep": target_pipeline(data["target_rep"], "Rep Code", data["mapping"]),
    "manager": target_pipeline(data["target_manager"], "Manager Code", data["mapping"]),
    "area": target_pipeline(data["target_area"], "Area Code", data["mapping"]),
}


# =========================
# 🎯 UI (TABS = CLEAN DASHBOARD)
# =========================
tab1, tab2, tab3, tab4 = st.tabs(["💰 Sales", "⚠️ Overdue", "🏦 Opening", "🎯 Targets"])


# =========================
# 💰 SALES
# =========================
with tab1:
    st.subheader("Rep")
    st.dataframe(sales["rep"], use_container_width=True)

    st.subheader("Manager")
    st.dataframe(sales["manager"], use_container_width=True)

    st.subheader("Area")
    st.dataframe(sales["area"], use_container_width=True)


# =========================
# ⚠️ OVERDUE
# =========================
with tab2:
    st.dataframe(overdue["rep"])
    st.dataframe(overdue["manager"])
    st.dataframe(overdue["area"])


# =========================
# 🏦 OPENING
# =========================
with tab3:
    st.dataframe(opening["rep"])
    st.dataframe(opening["manager"])
    st.dataframe(opening["area"])


# =========================
# 🎯 TARGETS
# =========================
with tab4:
    st.dataframe(targets["rep"])
    st.dataframe(targets["manager"])
    st.dataframe(targets["area"])
