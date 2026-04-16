import pandas as pd
import numpy as np
import streamlit as st

# =========================
# 📅 TIME SETTINGS
# =========================
current_month = pd.Timestamp.today().month
current_quarter = (current_month - 1) // 3 + 1


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

        "sales": pd.read_excel("Sales.xlsx", header=None),

        "mapping": pd.read_excel("Mapping.xlsx"),
        "codes": pd.read_excel("Code.xlsx"),

        "opening": pd.read_excel("Opening.xlsx", header=None),
        "overdue": pd.read_excel("Overdue.xlsx", header=None),

        "opening_detail": pd.read_excel("Opening Detail.xlsx", header=None),
    }


# =========================
# 🧠 FIX SALES COLUMNS
# =========================
def fix_sales_columns(sales):

    expected_cols = [
        'Date','Warehouse Name','Client Code','Client Name','Notes','MF','Mostanad',
        'Rep Code','Sales Unit Before Edit','Returns Unit Before Edit',
        'Sales Price','Invoice Discounts','Sales Value'
    ]

    sales = sales.iloc[:, :len(expected_cols)].copy()
    sales.columns = expected_cols

    return sales


# =========================
# 🚀 TARGET PIPELINE
# =========================
def build_target_pipeline(df, id_name, mapping):

    df = df.copy()
    mapping = mapping.copy()

    df.columns = df.columns.str.strip()
    mapping.columns = mapping.columns.str.strip()

    if "Product Code" not in df.columns:
        df["Product Code"] = np.nan

    if "Product Name" not in df.columns:
        df["Product Name"] = np.nan

    if "Sales Price" not in df.columns:
        df["Sales Price"] = 0

    df["Product Code"] = pd.to_numeric(df["Product Code"], errors="coerce")
    mapping["Product Code"] = pd.to_numeric(mapping["Product Code"], errors="coerce")

    mapping = mapping.drop_duplicates("Product Code")

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

    if "Product Name" in mapping.columns:
        df = df.merge(
            mapping[["Product Code", "Product Name"]],
            on="Product Code",
            how="left"
        )

    df["Target (Unit)"] = pd.to_numeric(df["Target (Unit)"], errors="coerce").fillna(0)
    df["Sales Price"] = pd.to_numeric(df["Sales Price"], errors="coerce").fillna(0)

    df["Value"] = df["Target (Unit)"] * df["Sales Price"]

    full = df.copy()
    month = df.copy()
    quarter = df.copy()
    ytd = df.copy()

    month["Value"] = month["Value"] * (current_month / 12)
    quarter["Value"] = quarter["Value"] * (current_quarter / 4)
    ytd["Value"] = ytd["Value"] * (current_month / 12)

    def group(d):
        return d.groupby([id_name], as_index=False)["Value"].sum()

    value_table = group(full).rename(columns={"Value": "Full Year 🏆"})
    value_table = value_table.merge(group(month).rename(columns={"Value": "Month 📅"}), on=id_name, how="left")
    value_table = value_table.merge(group(quarter).rename(columns={"Value": "Quarter 📊"}), on=id_name, how="left")
    value_table = value_table.merge(group(ytd).rename(columns={"Value": "YTD 📈"}), on=id_name, how="left")

    return {
        "value_table": value_table
    }


# =========================
# 🚀 OPENING DETAIL PIPELINE (FIXED & SAFE)
# =========================
def build_opening_detail_pipeline(opening_detail):

    df = opening_detail.copy()

    expected_cols = [
        'Branch',"Evak",'Opening Balance','Total Sales',
        'Returned Sales','Sales Value Before Extra Discounts',
        'Cash Collection',"Blank1",'Collection Checks',
        "Blank2",'Returned Chick','Collection Returned Chick',
        "Madinah",'Daienah','End Balance'
    ]

    # 🔥 SAFE FIX: handle mismatch instead of crash
    if df.shape[1] < len(expected_cols):
        # add missing columns
        for _ in range(len(expected_cols) - df.shape[1]):
            df[f"extra_{_}"] = np.nan

    df = df.iloc[:, :len(expected_cols)].copy()
    df.columns = expected_cols

    df['Client Code'] = None
    df['Client Name'] = None

    mask = df['Branch'].astype(str).str.strip() == "كود العميل"
    df.loc[mask, 'Client Code'] = df.loc[mask, 'Evak']
    df.loc[mask, 'Client Name'] = df.loc[mask, 'Opening Balance']

    df[['Client Code', 'Client Name']] = df[['Client Code', 'Client Name']].ffill()

    df = df[
        df['Branch'].notna() &
        (df['Branch'].astype(str).str.strip() != '') &
        (~df['Branch'].astype(str).str.contains(
            'نسبة العميل|كود العميل|اجماليات|كود الفرع',
            na=False
        ))
    ].copy()

    num_cols = [
        'Opening Balance','Total Sales','Returned Sales','Sales Value Before Extra Discounts',
        'Cash Collection','Collection Checks','Returned Chick','Collection Returned Chick',
        'Madinah','Daienah','End Balance'
    ]

    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    df['Client Code'] = df['Client Code'].astype(str)
    df['Client Name'] = df['Client Name'].astype(str).str.strip()

    def group(d, col):
        return d.groupby(col, as_index=False)[
            [
                'Opening Balance',
                'Total Sales',
                'Returned Sales',
                'Cash Collection',
                'Collection Checks',
                'End Balance'
            ]
        ].sum()

    return {
        "client": group(df, "Client Code"),
        "client_name": group(df, "Client Name"),
    }


# =========================
# 🎨 STREAMLIT UI
# =========================
st.set_page_config(layout="wide")
st.title("📊 Unified KPI System")

data = load_data()


# =========================
# 📦 OPENING DETAIL
# =========================
st.header("📦 OPENING DETAIL KPI")

opening_detail_result = build_opening_detail_pipeline(data["opening_detail"])

st.dataframe(opening_detail_result["client"])
st.dataframe(opening_detail_result["client_name"])
