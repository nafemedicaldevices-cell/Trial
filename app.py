```python
# =========================
# 📦 IMPORTS
# =========================
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")
st.title("📊 Sales Performance Dashboard")


# =========================
# 📅 TIME SETTINGS
# =========================
current_month = pd.Timestamp.today().month
current_quarter = (current_month - 1) // 3 + 1
past_quarters = max(current_quarter - 1, 0)


# =========================
# 📂 LOAD DATA
# =========================
@st.cache_data
def load_data():
    return {
        "sales": pd.read_excel("Sales.xlsx"),
        "overdue": pd.read_excel("Overdue.xlsx"),
        "opening": pd.read_excel("Opening.xlsx"),

        "target_manager": pd.read_excel("Target Manager.xlsx"),
        "target_area": pd.read_excel("Target Area.xlsx"),
        "target_rep": pd.read_excel("Target Rep.xlsx"),
        "target_supervisor": pd.read_excel("Target Supervisor.xlsx"),
        "target_evak": pd.read_excel("Target Evak.xlsx"),

        "mapping": pd.read_excel("Mapping.xlsx"),
        "codes": pd.read_excel("Code.xlsx")
    }

data = load_data()


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

    def group(d):
        return d.groupby([id_name], as_index=False)["Value"].sum()

    value_table = group(full).rename(columns={"Value": "Full Year 🏆"})
    value_table["Month 📅"] = group(month)["Value"]
    value_table["Quarter 📊"] = group(quarter)["Value"]
    value_table["YTD 📈"] = group(ytd)["Value"]

    def product_group(d):
        return d.groupby(
            [id_name, "Product Code", "Product Name"],
            as_index=False
        ).agg(
            Units=("Target (Unit)", "sum"),
            Value=("Value", "sum")
        )

    return {
        "value_table": value_table,
        "products_full": product_group(full),
        "products_month": product_group(month),
        "products_quarter": product_group(quarter),
        "products_ytd": product_group(ytd),
    }


# =========================
# 💰 SALES PIPELINE
# =========================
def build_sales_pipeline(sales, mapping, codes):

    sales = sales.copy()
    sales.columns = sales.columns.str.strip()

    if 'Old Product Code' not in sales.columns:
        sales['Old Product Code'] = np.nan

    if 'Date' in sales.columns:
        mask = sales['Date'].astype(str).str.strip().eq("كود الصنف")
        sales.loc[mask, 'Old Product Code'] = sales.loc[mask, 'Warehouse Name']
        sales['Old Product Code'] = sales['Old Product Code'].ffill()

    sales = sales[sales['Date'].notna()].copy()

    num_cols = [
        'Sales Unit Before Edit',
        'Returns Unit Before Edit',
        'Sales Price',
        'Invoice Discounts'
    ]

    for col in num_cols:
        if col in sales.columns:
            sales[col] = pd.to_numeric(sales[col], errors='coerce').fillna(0)

    sales['Old Product Code'] = pd.to_numeric(sales['Old Product Code'], errors='coerce')

    sales = sales.merge(mapping, on='Old Product Code', how='left')

    codes['Rep Code'] = pd.to_numeric(codes['Rep Code'], errors='coerce')
    sales = sales.merge(codes, on='Rep Code', how='left')

    sales['Total Sales Value'] = sales['Sales Unit Before Edit'] * sales['Sales Price']
    sales['Returns Value'] = sales['Returns Unit Before Edit'] * sales['Sales Price']
    sales['Sales After Returns'] = sales['Total Sales Value'] - sales['Returns Value']

    def group(df, cols):
        return df.groupby(cols, as_index=False)[
            ['Total Sales Value','Returns Value','Sales After Returns','Invoice Discounts']
        ].sum()

    return {
        "rep_value": group(sales, ['Rep Code']),
        "manager_value": group(sales, ['Manager Code']),
        "area_value": group(sales, ['Area Code']),
        "supervisor_value": group(sales, ['Supervisor Code']),
    }


# =========================
# ⏰ OVERDUE PIPELINE
# =========================
def build_overdue_pipeline(overdue, codes):

    overdue = overdue.iloc[:, :9].copy()

    overdue.columns = [
        "Client Name","Client Code","15 Days","30 Days","60 Days",
        "90 Days","120 Days","More Than 120 Days","Balance"
    ]

    for col in ["120 Days","More Than 120 Days"]:
        overdue[col] = pd.to_numeric(overdue[col], errors="coerce").fillna(0)

    overdue["Overdue"] = overdue["120 Days"] + overdue["More Than 120 Days"]

    overdue["Rep Code"] = pd.NA
    mask = overdue["Client Name"].astype(str).str.strip().eq("كود المندوب")
    overdue.loc[mask, "Rep Code"] = overdue.loc[mask, "Client Code"]
    overdue["Rep Code"] = overdue["Rep Code"].ffill()

    overdue["Rep Code"] = pd.to_numeric(overdue["Rep Code"], errors="coerce")
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")

    overdue = overdue.merge(codes, on="Rep Code", how="left")

    def group(level):
        return overdue.groupby(level)["Overdue"].sum().reset_index()

    return {
        "rep": group("Rep Code"),
        "manager": group("Manager Code"),
        "area": group("Area Code"),
        "supervisor": group("Supervisor Code")
    }


# =========================
# 🏦 OPENING PIPELINE
# =========================
def build_opening_pipeline(opening, codes):

    opening.columns = [
        'Branch',"Evak",'Opening Balance','Total Sales After Invoice Discounts',
        'Returns','Sales Value Before Extra Discounts',
        'Cash Collection','Collection Checks',
        'Returned Chick','Collection Returned Chick',
        "Extra Discounts",'Daienah','End Balance'
    ]

    opening["Rep Code"] = pd.NA

    mask = opening["Branch"].astype(str).str.strip().eq("كود المندوب")
    opening.loc[mask, "Rep Code"] = opening.loc[mask, "Opening Balance"]
    opening["Rep Code"] = opening["Rep Code"].ffill()

    opening["Rep Code"] = pd.to_numeric(opening["Rep Code"], errors="coerce")
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")

    opening = opening.merge(codes, on="Rep Code", how="left")

    def group(level):
        return opening.groupby(level)[
            ["Opening Balance","Cash Collection","Extra Discounts","End Balance"]
        ].sum().reset_index()

    return {
        "rep": group("Rep Code"),
        "manager": group("Manager Code"),
        "area": group("Area Code"),
        "supervisor": group("Supervisor Code")
    }


# =========================
# 🚀 RUN PIPELINES
# =========================
rep = build_target_pipeline(data["target_rep"], "Rep Code", data["mapping"])
manager = build_target_pipeline(data["target_manager"], "Manager Code", data["mapping"])
area = build_target_pipeline(data["target_area"], "Area Code", data["mapping"])
supervisor = build_target_pipeline(data["target_supervisor"], "Supervisor Code", data["mapping"])
evak = build_target_pipeline(data["target_evak"], "Evak Code", data["mapping"])

sales = build_sales_pipeline(data["sales"], data["mapping"], data["codes"])
overdue = build_overdue_pipeline(data["overdue"], data["codes"])
opening = build_opening_pipeline(data["opening"], data["codes"])


# =========================
# 📊 UI
# =========================
st.header("📊 TARGET KPI")
st.dataframe(rep["value_table"])

st.header("💰 SALES KPI")
st.dataframe(sales["rep_value"])

st.header("⏰ OVERDUE KPI")
st.dataframe(overdue["rep"])

st.header("🏦 OPENING KPI")
st.dataframe(opening["rep"])
```
