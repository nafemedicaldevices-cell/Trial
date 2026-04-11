import streamlit as st
import pandas as pd
import numpy as np

# =========================
# 🎨 APP SETUP
# =========================
st.set_page_config(layout="wide")
st.title("📊 Unified KPI Dashboard (ULTIMATE ROBUST VERSION)")


# =========================
# 🧠 ULTRA SMART EXCEL READER
# =========================
def smart_read(file):
    # اقرأ بدون افتراض headers
    raw = pd.read_excel(file, header=None)

    # امسح الصفوف الفاضية
    raw = raw.dropna(how="all")

    # حاول تلاقي صف الهيدر الحقيقي
    header_row = None

    for i in range(min(15, len(raw))):
        row = raw.iloc[i].astype(str)

        if (
            row.str.contains("كود|عميل|صنف|سعر|qty|sales|return", case=False).any()
        ):
            header_row = i
            break

    if header_row is not None:
        df = pd.read_excel(file, header=header_row)
    else:
        df = pd.read_excel(file)

    df.columns = df.columns.astype(str).str.strip()

    return df


# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    return {
        "sales": smart_read("Sales.xlsx"),
        "overdue": smart_read("Overdue.xlsx"),
        "opening": smart_read("Opening.xlsx"),
        "mapping": smart_read("Mapping.xlsx"),
        "codes": smart_read("Code.xlsx"),

        "target_rep": smart_read("Target Rep.xlsx"),
        "target_manager": smart_read("Target Manager.xlsx"),
        "target_area": smart_read("Target Area.xlsx"),
        "target_supervisor": smart_read("Target Supervisor.xlsx"),
    }

data = load_data()


# =========================
# HELPERS
# =========================
def to_numeric(df, cols):
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    return df


def find_col(df, keywords):
    for col in df.columns:
        col_str = str(col).lower()
        for k in keywords:
            if k.lower() in col_str:
                return col
    return None


def merge_codes(df, codes, key):
    if key not in df.columns:
        df[key] = pd.NA

    df[key] = pd.to_numeric(df[key], errors="coerce").astype("Int64")
    codes[key] = pd.to_numeric(codes[key], errors="coerce").astype("Int64")

    return df.merge(codes, on=key, how="left")


# =========================
# 🚀 SALES PIPELINE (AUTO FIX FINAL)
# =========================
def sales_pipeline(sales, mapping, codes):

    sales = sales.copy()

    # 🔥 detect ANY structure (Arabic / English)
    unit_col = find_col(sales, ["unit","qty","quantity","كمية","عدد"])
    price_col = find_col(sales, ["price","سعر","value","unit price"])
    return_col = find_col(sales, ["return","مرتجع","returns"])

    if unit_col is None or price_col is None:
        st.error("❌ Cannot detect Sales structure")
        st.write("Columns:", sales.columns.tolist())
        return {}

    sales[unit_col] = pd.to_numeric(sales[unit_col], errors="coerce").fillna(0)
    sales[price_col] = pd.to_numeric(sales[price_col], errors="coerce").fillna(0)

    if return_col:
        sales[return_col] = pd.to_numeric(sales[return_col], errors="coerce").fillna(0)
    else:
        sales["__return__"] = 0
        return_col = "__return__"

    sales = merge_codes(sales, codes, "Rep Code")

    sales["Total Sales"] = sales[unit_col] * sales[price_col]
    sales["Returns"] = sales[return_col] * sales[price_col]
    sales["Net Sales"] = sales["Total Sales"] - sales["Returns"]

    return {
        "rep": sales.groupby("Rep Code")[["Total Sales","Returns","Net Sales"]].sum().reset_index(),
        "manager": sales.groupby("Manager Code")[["Total Sales","Returns","Net Sales"]].sum().reset_index()
        if "Manager Code" in sales.columns else pd.DataFrame(),
        "area": sales.groupby("Area Code")[["Total Sales","Returns","Net Sales"]].sum().reset_index()
        if "Area Code" in sales.columns else pd.DataFrame(),
        "supervisor": sales.groupby("Supervisor Code")[["Total Sales","Returns","Net Sales"]].sum().reset_index()
        if "Supervisor Code" in sales.columns else pd.DataFrame(),
    }


# =========================
# ⚠️ OVERDUE PIPELINE
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
    mask = df["Client Name"].astype(str).str.contains("كود المندوب", na=False)

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
# 🏦 OPENING PIPELINE
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
    df.columns = df.columns.astype(str).str.strip()

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
# 🚀 RUN ALL
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
