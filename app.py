import streamlit as st
import pandas as pd
import numpy as np
import os

st.set_page_config(page_title="Client Harakah", layout="wide")
st.title("👤 Client Harakah Dashboard")

# =========================
# 📂 LOAD FUNCTION
# =========================
def load_client_haraka():

    file_path = "Client Harakah.xlsx"

    if not os.path.exists(file_path):
        st.error("❌ File not found: Client Harakah.xlsx")
        return pd.DataFrame()

    # =========================
    # 1️⃣ READ FILE
    # =========================
    df = pd.read_excel(file_path)

    # =========================
    # 2️⃣ RENAME COLUMNS SAFELY
    # =========================
    expected_cols = [
        "Client Code",
        "Client Name",
        "Opening Balance",
        "Sales Value",
        "Returns Value",
        "Tasweyat Madinah (Credit)",
        "Total Collection",
        "Madfoaat",
        "Tasweyat Madinah (Debit)",
        "End Balance",
        "Motalbet El Fatrah"
    ]

    df = df.iloc[:, :len(expected_cols)]
    df.columns = expected_cols[:df.shape[1]]

    # =========================
    # 3️⃣ NUMERIC CLEAN
    # =========================
    num_cols = [
        "Opening Balance",
        "Sales Value",
        "Returns Value",
        "Tasweyat Madinah (Credit)",
        "Total Collection",
        "Madfoaat",
        "Tasweyat Madinah (Debit)",
        "End Balance",
        "Motalbet El Fatrah"
    ]

    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # =========================
    # 4️⃣ REP EXTRACTION (FINAL SAFE VERSION)
    # =========================

    df["Rep Code"] = np.nan
    df["Rep Name"] = ""

    mask = df["Sales Value"].astype(str).str.contains("مندوب المبيعات", na=False)

    # 🔥 safe extraction
    rep_code = pd.to_numeric(df.loc[mask, "Returns Value"], errors="coerce").values.copy()
    rep_name = df.loc[mask, "Tasweyat Madinah (Credit)"].astype(str).values.copy()

    df.loc[mask, "Rep Code"] = rep_code
    df.loc[mask, "Rep Name"] = rep_name

    # 🔽 fill down
    df["Rep Code"] = df["Rep Code"].ffill()
    df["Rep Name"] = df["Rep Name"].ffill()

    # =========================
    # 5️⃣ REMOVE MARKER ROWS
    # =========================
    df = df[~df["Sales Value"].astype(str).str.contains("مندوب المبيعات", na=False)].copy()

    return df


# =========================
# 📥 RUN
# =========================
df = load_client_haraka()

# =========================
# 📊 UI
# =========================
if df.empty:
    st.warning("⚠️ No data loaded")
else:
    st.success("✅ Data Loaded Successfully")

    st.dataframe(df, use_container_width=True)

    st.subheader("📊 KPIs")

    c1, c2, c3 = st.columns(3)

    c1.metric("Sales", f"{df['Sales Value'].sum():,.0f}")
    c2.metric("Returns", f"{df['Returns Value'].sum():,.0f}")
    c3.metric("Net", f"{df['Sales Value'].sum() - df['Returns Value'].sum():,.0f}")
