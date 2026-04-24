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
        st.error("File not found")
        return pd.DataFrame()

    # =========================
    # 1️⃣ READ RAW (NO CLEANING)
    # =========================
    df = pd.read_excel(file_path, header=None)

    # =========================
    # 2️⃣ EXTRACT REP FIRST (IMPORTANT)
    # =========================
    rep_mask = df.astype(str).apply(
        lambda row: row.str.contains("مندوب المبيعات", na=False)
    ).any(axis=1)

    rep_row = df[rep_mask]

    if not rep_row.empty:
        r = rep_row.iloc[0]
        rep_code = r.iloc[4]
        rep_name = r.iloc[5]
    else:
        rep_code = np.nan
        rep_name = ""

    # =========================
    # 3️⃣ REMOVE REP ROWS
    # =========================
    df = df[~rep_mask].reset_index(drop=True)

    # =========================
    # 4️⃣ SET HEADERS
    # =========================
    df.columns = [
        "Client Code","Client Name","Opening Balance",
        "Sales Value","Returns Value",
        "Tasweyat Madinah (Credit)",
        "Total Collection","Madfoaat",
        "Tasweyat Madinah (Debit)",
        "End Balance","Motalbet El Fatrah"
    ]

    # =========================
    # 5️⃣ 🧹 REMOVE EMPTY ROWS (FIRST COLUMN CLEAN)
    # =========================
    first_col = df.columns[0]

    df[first_col] = df[first_col].astype(str)

    df = df[
        (df[first_col].notna()) &
        (df[first_col].str.strip() != "") &
        (~df[first_col].str.lower().isin(["none", "nan"]))
    ].copy()

    df = df.reset_index(drop=True)

    # =========================
    # 6️⃣ NUMERIC CLEAN
    # =========================
    num_cols = df.columns[2:]

    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # =========================
    # 7️⃣ ASSIGN REP
    # =========================
    df["Rep Code"] = rep_code
    df["Rep Name"] = rep_name

    return df


# =========================
# RUN
# =========================
df = load_client_haraka()

if df.empty:
    st.warning("No data found")
else:
    st.success("Loaded successfully")

    st.dataframe(df, use_container_width=True)

    st.subheader("KPIs")

    c1, c2, c3 = st.columns(3)

    c1.metric("Sales", f"{df['Sales Value'].sum():,.0f}")
    c2.metric("Returns", f"{df['Returns Value'].sum():,.0f}")
    c3.metric("Net", f"{df['Sales Value'].sum() - df['Returns Value'].sum():,.0f}")
