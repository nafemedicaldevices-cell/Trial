import pandas as pd
import numpy as np
import streamlit as st

# =========================
# 📅 TIME SETTINGS
# =========================
current_month = pd.Timestamp.today().month
current_quarter = (current_month - 1) // 3 + 1


# =========================
# 🧹 CLEAN DATA FUNCTION
# =========================
def clean_dataframe(df, rename_map=None, add_columns=None):

    df = df.copy()

    # 1️⃣ Rename columns
    if rename_map:
        df.rename(columns=rename_map, inplace=True)

    # 2️⃣ Add columns
    if add_columns:
        for col, val in add_columns.items():
            if col not in df.columns:
                df[col] = val

    # 3️⃣ Remove empty rows
    df.replace(r'^\s*$', np.nan, regex=True, inplace=True)
    df.dropna(how="all", inplace=True)

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

        "sales": pd.read_excel("Sales.xlsx", header=None),

        "mapping": pd.read_excel("Mapping.xlsx"),
        "codes": pd.read_excel("Code.xlsx"),

        "opening": pd.read_excel("Opening.xlsx", header=None),
        "overdue": pd.read_excel("Overdue.xlsx", header=None),
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

    def group(d):
        return d.groupby([id_name], as_index=False)["Value"].sum()

    value_table = group(df).rename(columns={"Value": "Full Year 🏆"})

    return {
        "value_table": value_table,
        "products_full": df.groupby(
            [id_name, "Product Code", "Product Name"],
            as_index=False
        ).agg(
            Units=("Target (Unit)", "sum"),
            Value=("Value", "sum")
        )
    }


# =========================
# 🚀 STREAMLIT UI
# =========================
st.set_page_config(layout="wide")
st.title("📊 Unified KPI System")

data = load_data()

# =========================
# 🧹 CLEAN TARGET DATA (NEW LAYER)
# =========================
target_rep_raw = clean_dataframe(data["target_rep"])
target_manager_raw = clean_dataframe(data["target_manager"])
target_area_raw = clean_dataframe(data["target_area"])
target_supervisor_raw = clean_dataframe(data["target_supervisor"])

# =========================
# 🎯 TARGET KPI
# =========================
st.header("🎯 TARGET KPI")

target_rep = build_target_pipeline(target_rep_raw, "Rep Code", data["mapping"])
target_manager = build_target_pipeline(target_manager_raw, "Manager Code", data["mapping"])
target_area = build_target_pipeline(target_area_raw, "Area Code", data["mapping"])
target_supervisor = build_target_pipeline(target_supervisor_raw, "Supervisor Code", data["mapping"])

st.dataframe(target_rep["value_table"])
st.dataframe(target_manager["value_table"])
st.dataframe(target_area["value_table"])
st.dataframe(target_supervisor["value_table"])


# =========================
# 📦 PRODUCTS
# =========================
st.header("📦 PRODUCTS")

st.dataframe(target_rep["products_full"])
st.dataframe(target_manager["products_full"])
st.dataframe(target_area["products_full"])
st.dataframe(target_supervisor["products_full"])


# =========================
# 💰 SALES
# =========================
st.header("💰 SALES KPI")

sales = fix_sales_columns(data["sales"])

st.dataframe(sales)


# =========================
# 📦 OPENING
# =========================
st.header("📦 OPENING KPI")
st.dataframe(data["opening"])


# =========================
# ⏳ OVERDUE
# =========================
st.header("⏳ OVERDUE KPI")
st.dataframe(data["overdue"])
