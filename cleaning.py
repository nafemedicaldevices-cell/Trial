import pandas as pd
import numpy as np

# =========================
# 📂 FILES
# =========================
FILES = {
    "Rep": "Target Rep.xlsx",
    "Manager": "Target Manager.xlsx",
    "Area": "Target Area.xlsx",
    "Supervisor": "Target Supervisor.xlsx",
    "Evak": "Target Evak.xlsx",
}

def load_and_process_data():

    all_data = []

    for level, file in FILES.items():

        df = pd.read_excel(file)
        df.columns = df.columns.str.strip()

        # =========================
        # 📌 FIXED COLUMNS
        # =========================
        fixed_cols = [
            "Year",
            "Product Code",
            "Old Product Name",
            "Sales Price"
        ]

        # =========================
        # 🔄 UNPIVOT
        # =========================
        df = df.melt(
            id_vars=fixed_cols,
            var_name="Code",
            value_name="Target (Year)"
        )

        df["Level"] = level

        # =========================
        # 🧹 CLEAN
        # =========================
        df["Target (Year)"] = pd.to_numeric(df["Target (Year)"], errors="coerce")

        # =========================
        # 📊 CALCULATIONS
        # =========================
        df["Target (Unit)"] = df["Target (Year)"] / 12
        df["Target (Value)"] = df["Target (Unit)"] * df["Sales Price"]

        # =========================
        # 📅 MONTHS EXPANSION
        # =========================
        months = [
            "Jan","Feb","Mar","Apr","May","Jun",
            "Jul","Aug","Sep","Oct","Nov","Dec"
        ]

        df_long = df.loc[df.index.repeat(12)].copy()
        df_long["Month"] = np.tile(months, len(df))

        df_long["Target (Unit)"] = np.repeat(df["Target (Unit)"].values, 12)
        df_long["Target (Value)"] = np.repeat(df["Target (Value)"].values, 12)

        all_data.append(df_long)

    final_df = pd.concat(all_data, ignore_index=True)

    # =========================
    # 📌 ORDER COLUMNS
    # =========================
    final_df = final_df[
        [
            "Level",
            "Code",
            "Year",
            "Month",
            "Product Code",
            "Old Product Name",
            "Sales Price",
            "Target (Year)",
            "Target (Unit)",
            "Target (Value)"
        ]
    ]
    #-------------------------------------------------------------------------------------------------------------------------------------
    import pandas as pd
import streamlit as st

st.title("📊 Rep Harakah Data Cleaner")

# =========================
# 📂 Upload File
# =========================
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:

    # =========================
    # 📥 Load Data
    # =========================
    df = pd.read_excel(uploaded_file, sheet_name="Rep Harakah")

    st.subheader("📌 Raw Data Preview")
    st.dataframe(df.head())

    # =========================
    # 🧹 Cleaning Steps
    # =========================

    # حذف أول صفّين
    df = df.iloc[2:].reset_index(drop=True)

    # حذف الصفوف الفاضية
    df = df.dropna(how="all")

    # تنظيف أسماء الأعمدة
    df.columns = df.columns.str.strip()

    # حذف الصفوف بدون Rep Code
    if "Rep Code" in df.columns:
        df = df[df["Rep Code"].notna()]

    # =========================
    # 📊 Result
    # =========================
    st.subheader("✅ Cleaned Data")
    st.dataframe(df)

    # =========================
    # ⬇️ Download
    # =========================
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Clean CSV",
        data=csv,
        file_name="clean_rep_data.csv",
        mime="text/csv"
    )

    return final_df
