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
    # 1️⃣ READ RAW FILE
    # =========================
    raw = pd.read_excel(file_path, header=None)

    # =========================
    # 2️⃣ FIND REP ROW (BEFORE ANY CLEANING)
    # =========================
    rep_mask = raw.astype(str).apply(
        lambda row: row.str.contains("مندوب المبيعات", na=False)
    ).any(axis=1)

    rep_row = raw[rep_mask]

    if not rep_row.empty:
        r = rep_row.iloc[0]
        rep_code = r.iloc[4]   # 10
        rep_name = r.iloc[5]   # باسم
    else:
        rep_code = np.nan
        rep_name = ""

    # =========================
    # 3️⃣ REMOVE REP ROW FROM DATA
    # =========================
    raw = raw[~rep_mask].reset_index(drop=True)

    # =========================
    # 4️⃣ SET COLUMNS
    # =========================
    raw.columns = [
        "Client Code","Client Name","Opening Balance",
        "Sales Value","Returns Value",
        "Tasweyat Madinah (Credit)",
        "Total Collection","Madfoaat",
        "Tasweyat Madinah (Debit)",
        "End Balance","Motalbet El Fatrah"
    ]

    # =========================
    # 5️⃣ ASSIGN REP FIRST (IMPORTANT STEP DONE FIRST)
    # =========================
    raw["Rep Code"] = rep_code
    raw["Rep Name"] = rep_name

    # =========================
    # 6️⃣ NOW SAFE TYPE CONVERSION
    # =========================
    num_cols = [
        "Opening Balance","Sales Value","Returns Value",
        "Tasweyat Madinah (Credit)","Total Collection",
        "Madfoaat","Tasweyat Madinah (Debit)",
        "End Balance","Motalbet El Fatrah"
    ]

    for col in num_cols:
        raw[col] = pd.to_numeric(raw[col], errors="coerce").fillna(0)

    # Rep columns after assignment
    raw["Rep Code"] = pd.to_numeric(raw["Rep Code"], errors="coerce")
    raw["Rep Name"] = raw["Rep Name"].astype(str)

    return raw


# =========================
# RUN
# =========================
df = load_client_haraka()

if df.empty:
    st.warning("No data")
else:
    st.success("Loaded successfully")

    st.dataframe(df, use_container_width=True)

    st.subheader("KPIs")

    c1, c2, c3 = st.columns(3)

    c1.metric("Sales", f"{df['Sales Value'].sum():,.0f}")
    c2.metric("Returns", f"{df['Returns Value'].sum():,.0f}")
    c3.metric("Net", f"{df['Sales Value'].sum() - df['Returns Value'].sum():,.0f}")
