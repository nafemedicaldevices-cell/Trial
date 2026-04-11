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
        "sales": pd.read_excel("Sales.xlsx"),
        "mapping": pd.read_excel("Mapping.xlsx"),
        "codes": pd.read_excel("Code.xlsx"),
    }

# =========================
# 🚀 TARGET PIPELINE (SAFE)
# =========================
def build_target_pipeline(df, id_name, mapping):

    df = df.copy()
    mapping = mapping.copy()

    df.columns = df.columns.str.strip()

    # SAFE KEYS
    if "Product Code" not in df.columns:
        df["Product Code"] = np.nan

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

    df = df.merge(mapping, on="Product Code", how="left")

    df["Target (Unit)"] = pd.to_numeric(df["Target (Unit)"], errors="coerce").fillna(0)
    df["Sales Price"] = pd.to_numeric(df["Sales Price"], errors="coerce").fillna(0)

    df["Full Value"] = df["Target (Unit)"] * df["Sales Price"]

    # TIME SPLIT
    full = df.copy()
    month = df.copy()
    quarter = df.copy()
    ytd = df.copy()

    month["Value"] = month["Full Value"] * (current_month / 12)
    quarter["Value"] = quarter["Full Value"] * (current_quarter / 4)
    ytd["Value"] = ytd["Full Value"] * (current_month / 12)
    full["Value"] = full["Full Value"]

    def group(d):
        if id_name not in d.columns:
            return pd.DataFrame(columns=[id_name, "Value"])
        return d.groupby([id_name], as_index=False)["Value"].sum()

    base = group(full).rename(columns={"Value": "Full Year 🏆"})

    base = base.merge(group(month).rename(columns={"Value": "Month 📅"}), on=id_name, how="left")
    base = base.merge(group(quarter).rename(columns={"Value": "Quarter 📊"}), on=id_name, how="left")
    base = base.merge(group(ytd).rename(columns={"Value": "YTD 📈"}), on=id_name, how="left")

    return base


# =========================
# 🚀 SALES PIPELINE (FULL SAFE FIX)
# =========================
def build_sales_pipeline(sales, mapping, codes):

    sales = sales.copy()
    sales.columns = sales.columns.str.strip()

    # =========================
    # 🛡️ SAFE COLUMN CREATION
    # =========================
    if "Rep Code" not in sales.columns:
        sales["Rep Code"] = np.nan

    if "Manager Code" not in sales.columns:
        sales["Manager Code"] = np.nan

    if "Area Code" not in sales.columns:
        sales["Area Code"] = np.nan

    if "Supervisor Code" not in sales.columns:
        sales["Supervisor Code"] = np.nan

    # =========================
    # 🔢 NUMERIC CLEAN
    # =========================
    num_cols = [
        "Sales Unit Before Edit",
        "Returns Unit Before Edit",
        "Sales Price",
        "Invoice Discounts"
    ]

    for col in num_cols:
        if col not in sales.columns:
            sales[col] = 0
        sales[col] = pd.to_numeric(sales[col], errors="coerce").fillna(0)

    # =========================
    # 🆔 IDS CLEAN
    # =========================
    sales["Rep Code"] = pd.to_numeric(sales["Rep Code"], errors="coerce")
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")

    sales = sales.merge(codes, on="Rep Code", how="left")

    # =========================
    # 💰 CALCULATIONS
    # =========================
    sales["Total Sales Value"] = sales["Sales Unit Before Edit"] * sales["Sales Price"]
    sales["Returns Value"] = sales["Returns Unit Before Edit"] * sales["Sales Price"]
    sales["Sales After Returns"] = sales["Total Sales Value"] - sales["Returns Value"]

    # =========================
    # 📊 SAFE GROUP ENGINE
    # =========================
    def safe_group(df, group_cols, sum_cols):

        group_cols = [c for c in group_cols if c in df.columns]
        sum_cols = [c for c in sum_cols if c in df.columns]

        if not group_cols:
            return pd.DataFrame()

        return df.groupby(group_cols, as_index=False)[sum_cols].sum()

    return {
        "rep_value": safe_group(sales, ["Rep Code"], ["Total Sales Value","Returns Value","Sales After Returns"]),
        "manager_value": safe_group(sales, ["Manager Code"], ["Total Sales Value","Returns Value","Sales After Returns"]),
        "area_value": safe_group(sales, ["Area Code"], ["Total Sales Value","Returns Value","Sales After Returns"]),
        "supervisor_value": safe_group(sales, ["Supervisor Code"], ["Total Sales Value","Returns Value","Sales After Returns"]),
    }


# =========================
# 🎨 STREAMLIT UI
# =========================
st.set_page_config(layout="wide")
st.title("📊 Unified KPI System (ERROR-FREE VERSION)")

data = load_data()

# =========================
# 🎯 TARGET
# =========================
st.header("🎯 TARGET KPI")

st.dataframe(build_target_pipeline(data["target_rep"], "Rep Code", data["mapping"]))
st.dataframe(build_target_pipeline(data["target_manager"], "Manager Code", data["mapping"]))
st.dataframe(build_target_pipeline(data["target_area"], "Area Code", data["mapping"]))
st.dataframe(build_target_pipeline(data["target_supervisor"], "Supervisor Code", data["mapping"]))
st.dataframe(build_target_pipeline(data["target_evak"], "Evak Code", data["mapping"]))

# =========================
# 💰 SALES
# =========================
st.header("💰 SALES KPI")

sales = build_sales_pipeline(data["sales"], data["mapping"], data["codes"])

st.dataframe(sales["rep_value"], use_container_width=True)
st.dataframe(sales["manager_value"], use_container_width=True)
st.dataframe(sales["area_value"], use_container_width=True)
st.dataframe(sales["supervisor_value"], use_container_width=True)
