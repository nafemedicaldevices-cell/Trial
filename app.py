```python
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
        "sales": pd.read_excel("Sales.xlsx"),
        "mapping": pd.read_excel("Mapping.xlsx"),
        "codes": pd.read_excel("Code.xlsx"),
    }

# =========================
# 🚀 TARGET PIPELINE
# =========================
def build_target_pipeline(df, id_name, mapping):

    df = df.copy()
    mapping = mapping.copy()

    df.columns = df.columns.str.strip()

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
# 🚀 SALES PIPELINE (FIXED)
# =========================
def build_sales_pipeline(sales, mapping, codes):

    sales = sales.copy()
    codes = codes.copy()

    sales.columns = sales.columns.str.strip()
    codes.columns = codes.columns.str.strip()

    # =========================
    # 🛡️ SAFE COLUMNS
    # =========================
    for col in ["Rep Code", "Manager Code", "Area Code", "Supervisor Code"]:
        if col not in sales.columns:
            sales[col] = np.nan

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
    # 🆔 CLEAN IDS
    # =========================
    sales["Rep Code"] = pd.to_numeric(sales["Rep Code"], errors="coerce")
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")

    # 🔥 DEBUG قبل الميرج
    st.subheader("🔍 DEBUG SALES")
    st.write("Sales shape:", sales.shape)
    st.write("Codes shape:", codes.shape)
    st.write("Sales Rep unique:", sales["Rep Code"].nunique())
    st.write("Codes Rep unique:", codes["Rep Code"].nunique())

    # =========================
    # 🔗 MERGE (CRITICAL FIX)
    # =========================
    sales = sales.merge(codes, on="Rep Code", how="inner")

    st.write("After merge shape:", sales.shape)

    # لو فاضي → وقف
    if sales.empty:
        st.error("❌ المشكلة: مفيش تطابق بين Sales و Code")
        return {
            "rep_value": pd.DataFrame(),
            "manager_value": pd.DataFrame(),
            "area_value": pd.DataFrame(),
            "supervisor_value": pd.DataFrame(),
        }

    # =========================
    # 💰 CALCULATIONS
    # =========================
    sales["Total Sales Value"] = sales["Sales Unit Before Edit"] * sales["Sales Price"]
    sales["Returns Value"] = sales["Returns Unit Before Edit"] * sales["Sales Price"]
    sales["Sales After Returns"] = sales["Total Sales Value"] - sales["Returns Value"]

    # =========================
    # 📊 GROUP
    # =========================
    def safe_group(df, group_cols):

        group_cols = [c for c in group_cols if c in df.columns]

        if not group_cols:
            return pd.DataFrame()

        return df.groupby(group_cols, as_index=False)[
            ["Total Sales Value", "Returns Value", "Sales After Returns"]
        ].sum()

    return {
        "rep_value": safe_group(sales, ["Rep Code"]),
        "manager_value": safe_group(sales, ["Manager Code"]),
        "area_value": safe_group(sales, ["Area Code"]),
        "supervisor_value": safe_group(sales, ["Supervisor Code"]),
    }


# =========================
# 🎨 STREAMLIT UI
# =========================
st.set_page_config(layout="wide")
st.title("📊 Unified KPI System (FINAL FIX)")

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
```
