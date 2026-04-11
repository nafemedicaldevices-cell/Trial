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
        "mapping": pd.read_excel("Mapping.xlsx"),
        "codes": pd.read_excel("Code.xlsx"),
        "target_rep": pd.read_excel("Target Rep.xlsx"),
    }

# =========================
# 🎯 TARGET PIPELINE
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

    def group(d):
        return d.groupby([id_name], as_index=False)["Value"].sum()

    value_table = group(full).rename(columns={"Value": "Full Year"})
    value_table["Month"] = group(month)["Value"]
    value_table["Quarter"] = group(quarter)["Value"]
    value_table["YTD"] = group(ytd)["Value"]

    return value_table

# =========================
# 💰 SALES PIPELINE
# =========================
def build_sales_pipeline(sales):

    sales = sales.copy()
    sales.columns = sales.columns.str.strip()

    sales['Total Sales Value'] = sales['Sales Unit Before Edit'] * sales['Sales Price']
    sales['Returns Value'] = sales['Returns Unit Before Edit'] * sales['Sales Price']
    sales['Sales After Returns'] = sales['Total Sales Value'] - sales['Returns Value']

    return sales.groupby("Rep Code", as_index=False)[
        ["Total Sales Value","Returns Value","Sales After Returns","Invoice Discounts"]
    ].sum()

# =========================
# ⏰ OVERDUE
# =========================
def build_overdue(overdue):

    overdue.columns = [
        "Client Name","Client Code","15","30","60","90","120","120+","Balance"
    ]

    overdue["Overdue"] = overdue["120"] + overdue["120+"]

    return overdue.groupby("Client Code", as_index=False)["Overdue"].sum()

# =========================
# 🏦 OPENING
# =========================
def build_opening(opening):

    opening.columns = [
        'Branch',"Evak",'Opening Balance','Sales','Returns','Before Discount',
        'Cash','Checks','Returned','Returned2',"Extra",'Daienah','End'
    ]

    return opening.groupby("Branch", as_index=False)[
        ["Opening Balance","Cash","Checks","Extra","End"]
    ].sum()

# =========================
# 🚀 STREAMLIT APP
# =========================
st.set_page_config(layout="wide")
st.title("📊 Full Dashboard")

data = load_data()

# TARGET
st.header("🎯 Target")
target = build_target_pipeline(data["target_rep"], "Rep Code", data["mapping"])
st.dataframe(target, use_container_width=True)

# SALES
st.header("💰 Sales")
sales = build_sales_pipeline(data["sales"])
st.dataframe(sales, use_container_width=True)

# OVERDUE
st.header("⏰ Overdue")
overdue = build_overdue(data["overdue"])
st.dataframe(overdue, use_container_width=True)

# OPENING
st.header("🏦 Opening")
opening = build_opening(data["opening"])
st.dataframe(opening, use_container_width=True)
