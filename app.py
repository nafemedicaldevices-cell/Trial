import pandas as pd
import streamlit as st

# =========================
# 🟢 TITLE
# =========================
st.title("📊 KPI Dashboard - Target System")

# =========================
# 📂 LOAD ALL SHEETS
# =========================
@st.cache_data
def load_data():
    file = pd.ExcelFile("Target Rep.xlsx")

    df_list = []

    for sheet in file.sheet_names:
        df = pd.read_excel(file, sheet_name=sheet)
        df["Source Sheet"] = sheet
        df_list.append(df)

    return pd.concat(df_list, ignore_index=True)

df = load_data()

# =========================
# 📌 FIXED COLUMNS
# =========================
fixed_cols = ["Year", "Product Code", "Old Product Name", "Sales Price", "Source Sheet"]
level_cols = [col for col in df.columns if col not in fixed_cols]

# =========================
# 🔄 UNPIVOT
# =========================
df_melted = df.melt(
    id_vars=fixed_cols,
    value_vars=level_cols,
    var_name="Code",
    value_name="Target (Year)"
)

# =========================
# 🏷️ LEVEL
# =========================
df_melted["Level"] = df_melted["Source Sheet"]

# =========================
# 🧮 CLEAN + CALCULATIONS
# =========================
df_melted["Target (Year)"] = pd.to_numeric(df_melted["Target (Year)"], errors="coerce")

df_melted["Target (Unit)"] = df_melted["Target (Year)"] / 12
df_melted["Target (Value)"] = df_melted["Target (Unit)"] * df_melted["Sales Price"]

# =========================
# 🧹 FINAL TABLE
# =========================
df_final = df_melted[
    [
        "Year",
        "Product Code",
        "Old Product Name",
        "Sales Price",
        "Level",
        "Code",
        "Target (Year)",
        "Target (Unit)",
        "Target (Value)"
    ]
]

# =========================
# 🎛️ FILTERS
# =========================
st.sidebar.header("🔎 Filters")

year_filter = st.sidebar.multiselect("Year", df_final["Year"].dropna().unique())
level_filter = st.sidebar.multiselect("Level", df_final["Level"].dropna().unique())

filtered_df = df_final.copy()

if year_filter:
    filtered_df = filtered_df[filtered_df["Year"].isin(year_filter)]

if level_filter:
    filtered_df = filtered_df[filtered_df["Level"].isin(level_filter)]

# =========================
# 📊 KPIs
# =========================
st.subheader("📌 KPI Summary")

col1, col2, col3 = st.columns(3)

col1.metric("Total Target (Year)", f"{filtered_df['Target (Year)'].sum():,.0f}")
col2.metric("Total Target (Unit)", f"{filtered_df['Target (Unit)'].sum():,.0f}")
col3.metric("Total Value", f"{filtered_df['Target (Value)'].sum():,.0f}")

# =========================
# 📋 TABLE
# =========================
st.subheader("📋 Detailed Data")
st.dataframe(filtered_df, use_container_width=True)

# =========================
# 💾 DOWNLOAD
# =========================
csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇️ Download Data",
    csv,
    "kpi_output.csv",
    "text/csv"
)
