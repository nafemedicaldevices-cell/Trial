import streamlit as st
import pandas as pd
import numpy as np
import os

st.set_page_config(page_title="Client Harakah", layout="wide")
st.title("👤 Client Harakah Dashboard")

# =========================
# 📂 LOAD CLIENT HARKAH
# =========================
def load_client_haraka():

    file_path = "Client Harakah.xlsx"

    if not os.path.exists(file_path):
        st.error("❌ File not found: Client Harakah.xlsx")
        return pd.DataFrame()

    df = pd.read_excel(file_path)

    # =========================
    # 🧹 CLEAN FIRST COLUMN
    # =========================
    first_col = df.columns[0]
    df[first_col] = df[first_col].astype(str)

    df = df[
        df[first_col].notna() &
        (df[first_col].str.strip() != "") &
        (~df[first_col].str.contains("كود الفرع", na=False)) &
        (~df[first_col].str.contains("كود العميل", na=False))
    ].copy()

    df = df.reset_index(drop=True)

    # =========================
    # 🧾 SAFE RENAME
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
    # 🧠 EXTRACT REP
    # =========================
    marker = df["Sales Value"].astype(str).str.contains("مندوب المبيعات", na=False)

    df["Rep Code"] = np.where(marker, df["Returns Value"], np.nan)
    df["Rep Name"] = np.where(marker, df["Tasweyat Madinah (Credit)"], np.nan)

    df["Rep Code"] = df["Rep Code"].ffill()
    df["Rep Name"] = df["Rep Name"].ffill()

    # =========================
    # 🔢 NUMERIC FIX
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

    return df


# =========================
# 📥 LOAD DATA
# =========================
client_haraka = load_client_haraka()

# =========================
# 📊 DISPLAY
# =========================
st.subheader("📋 Data Preview")

if client_haraka.empty:
    st.warning("No data loaded")
else:
    st.dataframe(client_haraka, use_container_width=True)

    st.subheader("📊 KPIs")

    c1, c2, c3 = st.columns(3)

    c1.metric("Sales Value", f"{client_haraka['Sales Value'].sum():,.0f}")
    c2.metric("Returns", f"{client_haraka['Returns Value'].sum():,.0f}")
    c3.metric("Net", f"{(client_haraka['Sales Value'].sum() - client_haraka['Returns Value'].sum()):,.0f}")
