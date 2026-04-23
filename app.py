import pandas as pd
import numpy as np
import streamlit as st

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

        "opening": pd.read_excel("Opening.xlsx"),
        "overdue": pd.read_excel("Overdue.xlsx"),
    }


# =========================
# 🧹 CLEAN FUNCTION
# =========================
def clean_df(df):
    if df is None:
        return pd.DataFrame()

    df = df.dropna(how="all")
    df = df.replace(r'^\s*$', np.nan, regex=True)
    df = df.dropna(how="all")
    return df


# =========================
# 🏷️ RENAME COLUMNS
# =========================
def rename_columns(data):

    data["sales"].columns = [
        'Date','Warehouse Name','Client Code','Client Name','Notes','MF','Mostanad',
        'Rep Code','Sales Unit Before Edit','Returns Unit Before Edit',
        'Sales Price','Invoice Discounts','Sales Value'
    ]

    data["opening"].columns = [
        'Branch',"Evak",'Opening Balance','Total Sales',
        'Returns','Sales Value Before Extra Discounts',
        'Cash Collection','Collection Checks',
        'Returned Chick','Collection Returned Chick',
        "Madinah",'Daienah','End Balance'
    ]

    data["overdue"].columns = [
        "Client Name", "Client Code", "30 Days", "60 Days", "90 Days", "120 Days",
        "150 Days", "More Than 150 Days", "Balance"
    ]

    return data


# =========================
# ➕ ADD COLUMNS (FIXED)
# =========================
def add_columns(data):

    # ================= SALES =================
    df = data["sales"].copy()

    df["Sales Unit Before Edit"] = pd.to_numeric(df["Sales Unit Before Edit"], errors="coerce").fillna(0)
    df["Returns Unit Before Edit"] = pd.to_numeric(df["Returns Unit Before Edit"], errors="coerce").fillna(0)
    df["Sales Price"] = pd.to_numeric(df["Sales Price"], errors="coerce").fillna(0)

    df["Total Sales Value"] = df["Sales Unit Before Edit"] * df["Sales Price"]
    df["Returns Value"] = df["Returns Unit Before Edit"] * df["Sales Price"]
    df["Net Sales Value"] = df["Total Sales Value"] - df["Returns Value"]

    data["sales"] = df


    # ================= OPENING =================
    df = data["opening"].copy()

    for col in ["Total Sales", "Returns", "Cash Collection", "Collection Checks"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["Total Collection"] = df["Cash Collection"] + df["Collection Checks"]
    df["Sales After Returns"] = df["Total Sales"] - df["Returns"]

    data["opening"] = df


    # ================= OVERDUE =================
    df = data["overdue"].copy()

    aging_cols = ["30 Days","60 Days","90 Days","120 Days","150 Days","More Than 150 Days"]

    for col in aging_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["Overdue Value"] = df[["120 Days","150 Days","More Than 150 Days"]].sum(axis=1)
    df["Total Balance"] = df[aging_cols].sum(axis=1)

    data["overdue"] = df

    return data


# =========================
# 🧹 FINAL CLEAN
# =========================
def remove_empty_rows(data):
    for key in data:
        data[key] = clean_df(data[key])
    return data


# =========================
# 🚀 STREAMLIT APP
# =========================
st.set_page_config(layout="wide")
st.title("📊 KPI SYSTEM")

# =========================
# ▶️ PIPELINE RUN
# =========================
data = load_data()
data = rename_columns(data)
data = add_columns(data)
data = remove_empty_rows(data)


# =========================
# 🧪 DEBUG (IMPORTANT)
# =========================
st.subheader("🔍 DEBUG")

st.write("Sales shape:", data["sales"].shape)
st.write("Opening shape:", data["opening"].shape)
st.write("Overdue shape:", data["overdue"].shape)


# =========================
# 📊 DISPLAY
# =========================
st.header("📌 SALES")
st.dataframe(data["sales"])

st.header("📦 OPENING")
st.dataframe(data["opening"])

st.header("⏳ OVERDUE")
st.dataframe(data["overdue"])
