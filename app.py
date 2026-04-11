import streamlit as st
import pandas as pd
import numpy as np

# =========================
# 🎨 APP SETUP
# =========================
st.set_page_config(layout="wide")
st.title("📊 Unified KPI Dashboard (FINAL FIXED VERSION)")


# =========================
# 📥 LOAD DATA
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
# 🧠 HELPERS
# =========================
def to_numeric(df, cols):
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    return df


def merge_codes(df, codes, key):
    df = df.copy()
    codes = codes.copy()

    if key not in df.columns:
        df[key] = pd.NA

    df[key] = pd.to_numeric(df[key], errors="coerce").astype("Int64")
    codes[key] = pd.to_numeric(codes[key], errors="coerce").astype("Int64")

    return df.merge(codes, on=key, how="left")


def find_col(df, options):
    for c in options:
        if c in df.columns:
            return c
    return None


# =========================
# 🚀 SALES PIPELINE
# =========================
def sales_pipeline(sales, mapping, codes):

    sales = sales.copy()
    sales.columns = sales.columns.str.strip()

    unit_col = find_col(sales, ["Sales Unit Before Edit", "Sales Unit", "Units", "Qty"])
    return_col = find_col(sales, ["Returns Unit Before Edit", "Returns Unit", "Returns"])
    price_col = find_col(sales, ["Sales Price", "Price", "Unit Price"])

    if unit_col is None or price_col is None:
        st.error("❌ Missing Sales columns")
        st.write(sales.columns)
        return {}

    for c in [unit_col, return_col, price_col]:
        if c:
            sales[c] = pd.to_numeric(sales[c], errors="coerce").fillna(0)

    sales = merge_codes(sales, codes, "Rep Code")

    sales["Total Sales Value"] = sales[unit_col] * sales[price_col]
    sales["Returns Value"] = sales[return_col] * sales[price_col] if return_col else 0
    sales["Net Sales"] = sales["Total Sales Value"] - sales["Returns Value"]

    result = {
        "rep": sales.groupby("Rep Code")[["Total Sales Value","Returns Value","Net Sales"]].sum().reset_index()
    }

    if "Manager Code" in sales.columns:
        result["manager"] = sales.groupby("Manager Code")[["Total Sales Value","Returns Value","Net Sales"]].sum().reset_index()

    if "Area Code" in sales.columns:
        result["area"] = sales.groupby("Area Code")[["Total Sales Value","Returns Value","Net Sales"]].sum().reset_index()

    if "Supervisor Code" in sales.columns:
        result["supervisor"] = sales.groupby("Supervisor Code")[["Total Sales Value","Returns Value","Net Sales"]].sum().reset_index()

    return result


# =========================
# ⚠️ OVERDUE PIPELINE (FIXED)
# =========================
def overdue_pipeline(df, codes):

    df = df.copy()
    df = df.iloc[:, :9]

    df.columns = [
        "Client Name","Client Code","15","30","60","90","120","120+","Balance"
    ]

    for c in ["120","120+","Balance"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    df["Overdue"] = df["120"] + df["120+"]

    df["Rep Code"] = pd.NA
    mask = df["Client Name"].astype(str).str.strip().eq("كود المندوب")

    if mask.any():
        df.loc[mask, "Rep Code"] = df.loc[mask, "Client Code"]
        df["Rep Code"] = df["Rep Code"].ffill()

    df = merge_codes(df, codes, "Rep Code")

    if "Rep Code" not in df.columns:
        df["Rep Code"] = "Unknown"

    def safe_group(col):
        if col not in df.columns:
            return pd.DataFrame()
        return df.groupby(col)["Overdue"].sum().reset_index()

    return {
        "rep": safe_group("Rep Code"),
        "manager": safe_group("Manager Code"),
        "area": safe_group("Area Code"),
        "supervisor": safe_group("Supervisor Code"),
    }


# =========================
# 🏦 OPENING PIPELINE (FIXED GROUPBY)
# =========================
def opening_pipeline(df, codes):

    df = df.copy()

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

    df = merge_codes(df, codes, "Rep Code")

    if "Rep Code" not in df.columns:
        df["Rep Code"] = "Unknown"

    def safe_group(col):
        if col not in df.columns:
            return pd.DataFrame()

        return df.groupby(col)[
            ["Opening Balance","Total Collection","End Balance"]
        ].sum().reset_index()

    return {
        "rep": safe_group("Rep Code"),
        "manager": safe_group("Manager Code"),
        "area": safe_group("Area Code"),
        "supervisor": safe_group("Supervisor Code"),
    }


# =========================
# 🎯 TARGET PIPELINE
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
# 🚀 RUN PIPELINES
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
# 🎯 UI
# =========================
tab1, tab2, tab3, tab4 = st.tabs(["💰 Sales", "⚠️ Overdue", "🏦 Opening", "🎯 Targets"])


with tab1:
    st.subheader("Rep")
    st.dataframe(sales.get("rep", pd.DataFrame()), use_container_width=True)
    st.subheader("Manager")
    st.dataframe(sales.get("manager", pd.DataFrame()), use_container_width=True)
    st.subheader("Area")
    st.dataframe(sales.get("area", pd.DataFrame()), use_container_width=True)
    st.subheader("Supervisor")
    st.dataframe(sales.get("supervisor", pd.DataFrame()), use_container_width=True)


with tab2:
    st.dataframe(overdue.get("rep", pd.DataFrame()))
    st.dataframe(overdue.get("manager", pd.DataFrame()))
    st.dataframe(overdue.get("area", pd.DataFrame()))
    st.dataframe(overdue.get("supervisor", pd.DataFrame()))


with tab3:
    st.dataframe(opening.get("rep", pd.DataFrame()))
    st.dataframe(opening.get("manager", pd.DataFrame()))
    st.dataframe(opening.get("area", pd.DataFrame()))
    st.dataframe(opening.get("supervisor", pd.DataFrame()))


with tab4:
    st.dataframe(targets["rep"])
    st.dataframe(targets["manager"])
    st.dataframe(targets["area"])
