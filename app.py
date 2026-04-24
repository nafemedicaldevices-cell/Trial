import streamlit as st
import pandas as pd
import numpy as np
import os

st.set_page_config(page_title="Client Harakah", layout="wide")
st.title("👤 Client Harakah Dashboard")

# =========================
# 📂 LOAD
# =========================
def load_client_haraka():

    file_path = "Client Harakah.xlsx"

    if not os.path.exists(file_path):
        st.error("File not found")
        return pd.DataFrame()

    df = pd.read_excel(file_path, header=None)

    # =========================
    # 🧠 1. EXTRACT REP FROM FIRST METADATA ROW
    # =========================
    meta_row = df.iloc[0]

    rep_code = meta_row[4]   # "10"
    rep_name = meta_row[5]   # "باسم"

    # =========================
    # 🧹 REMOVE FIRST ROW (metadata row)
    # =========================
    df = df.iloc[1:].reset_index(drop=True)

    # =========================
    # 🧾 SET HEADERS
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
    # 🔢 NUMERIC CLEAN
    # =========================
    for c in df.columns[2:]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    # =========================
    # 🧠 ASSIGN REP (SAFE)
    # =========================
    df["Rep Code"] = rep_code
    df["Rep Name"] = rep_name

    return df


# =========================
# RUN
# =========================
df = load_client_haraka()

if df.empty:
    st.warning("No data")
else:
    st.success("Loaded")

    st.dataframe(df, use_container_width=True)

    st.subheader("KPIs")

    c1, c2, c3 = st.columns(3)

    c1.metric("Sales", f"{df['Sales Value'].sum():,.0f}")
    c2.metric("Returns", f"{df['Returns Value'].sum():,.0f}")
    c3.metric("Net", f"{df['Sales Value'].sum() - df['Returns Value'].sum():,.0f}")
