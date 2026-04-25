import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("📊 Sales Dashboard - Multi Level Targets")

# =========================
# 📂 LOAD CODES (HIERARCHY)
# =========================
codes = pd.read_excel("Code.xlsx")
codes.columns = codes.columns.str.strip()

codes["Rep Code"] = codes["Rep Code"].astype(str).str.strip()

# =========================
# 🎯 FILTERS (HIERARCHY)
# =========================
st.sidebar.header("Filters")

rep_list = sorted(codes["Rep Name"].dropna().unique())
sup_list = sorted(codes["Supervisor Name"].dropna().unique())
manager_list = sorted(codes["Manager Name"].dropna().unique())
area_list = sorted(codes["Area Name"].dropna().unique())

rep_filter = st.sidebar.multiselect("Rep", rep_list)
sup_filter = st.sidebar.multiselect("Supervisor", sup_list)
manager_filter = st.sidebar.multiselect("Manager", manager_list)
area_filter = st.sidebar.multiselect("Area", area_list)

# =========================
# 🔥 FILTER CODES
# =========================
filtered_codes = codes.copy()

if rep_filter:
    filtered_codes = filtered_codes[filtered_codes["Rep Name"].isin(rep_filter)]

if sup_filter:
    filtered_codes = filtered_codes[filtered_codes["Supervisor Name"].isin(sup_filter)]

if manager_filter:
    filtered_codes = filtered_codes[filtered_codes["Manager Name"].isin(manager_filter)]

if area_filter:
    filtered_codes = filtered_codes[filtered_codes["Area Name"].isin(area_filter)]

valid_reps = filtered_codes["Rep Code"].astype(str).str.strip().unique()

# =========================
# 📂 LOAD TARGETS (ALL LEVELS)
# =========================
def load_targets():

    FILES = {
        "Rep": "Target Rep.xlsx",
        "Supervisor": "Target Supervisor.xlsx",
        "Manager": "Target Manager.xlsx",
        "Area": "Target Area.xlsx"
    }

    all_targets = {}

    for level, file in FILES.items():

        sheets = pd.read_excel(file, sheet_name=None)

        level_data = []

        for sheet_name, df in sheets.items():

            df.columns = df.columns.str.strip()

            fixed_cols = ["Year", "Product Code", "Old Product Name", "Sales Price"]

            df = df.melt(
                id_vars=fixed_cols,
                var_name="Code",
                value_name="Target (Year)"
            )

            df["Target (Year)"] = pd.to_numeric(df["Target (Year)"], errors="coerce")

            df["Target (Unit)"] = df["Target (Year)"] / 12
            df["Target (Value)"] = df["Target (Unit)"] * df["Sales Price"]

            months = [
                "Jan","Feb","Mar","Apr","May","Jun",
                "Jul","Aug","Sep","Oct","Nov","Dec"
            ]

            df_long = df.loc[df.index.repeat(12)].copy()

            df_long["Month"] = months * len(df)

            df_long["Target (Unit)"] = df["Target (Unit)"].repeat(12).values
            df_long["Target (Value)"] = df["Target (Value)"].repeat(12).values

            df_long["Level"] = level

            level_data.append(df_long)

        all_targets[level] = pd.concat(level_data, ignore_index=True)

    return all_targets


targets = load_targets()

# =========================
# 🎯 SELECT TARGET LEVEL
# =========================
target_level = st.sidebar.selectbox(
    "Target Level",
    ["Rep", "Supervisor", "Manager", "Area"]
)

target_df = targets[target_level].copy()
target_df["Code"] = target_df["Code"].astype(str).str.strip()

# فلترة حسب hierarchy
target_df = target_df[target_df["Code"].isin(valid_reps)]

# =========================
# 🗓️ PERIOD
# =========================
period_type = st.sidebar.selectbox(
    "Period",
    ["Monthly", "Quarterly", "YTD", "Full Year"]
)

month_order = [
    "Jan","Feb","Mar","Apr","May","Jun",
    "Jul","Aug","Sep","Oct","Nov","Dec"
]

selected_month = st.sidebar.selectbox("Month", month_order)

quarter_map = {
    "Q1": ["Jan","Feb","Mar"],
    "Q2": ["Apr","May","Jun"],
    "Q3": ["Jul","Aug","Sep"],
    "Q4": ["Oct","Nov","Dec"]
}

selected_quarter = st.sidebar.selectbox("Quarter", list(quarter_map.keys()))

# =========================
# 🎯 TARGET CALCULATION
# =========================
if period_type == "Monthly":

    target_value = target_df[
        target_df["Month"] == selected_month
    ]["Target (Value)"].sum()

elif period_type == "Quarterly":

    target_value = target_df[
        target_df["Month"].isin(quarter_map[selected_quarter])
    ]["Target (Value)"].sum()

elif period_type == "YTD":

    idx = month_order.index(selected_month) + 1
    months = month_order[:idx]

    target_value = target_df[
        target_df["Month"].isin(months)
    ]["Target (Value)"].sum()

else:

    target_value = target_df["Target (Value)"].sum()

# =========================
# 📊 OUTPUT
# =========================
st.subheader("🎯 Target Result")

st.metric("Target Value", f"{target_value:,.0f}")

st.dataframe(target_df, use_container_width=True)
