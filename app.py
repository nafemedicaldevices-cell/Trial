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
        st.error("❌ File not found")
        return pd.DataFrame()

    df = pd.read_excel(file_path)

    # =========================
    # 🧾 RENAME
    # =========================
    cols = [
        "Client Code","Client Name","Opening Balance",
        "Sales Value","Returns Value",
        "Tasweyat Madinah (Credit)",
        "Total Collection","Madfoaat",
        "Tasweyat Madinah (Debit)",
        "End Balance","Motalbet El Fatrah"
    ]

    df = df.iloc[:, :len(cols)]
    df.columns = cols[:df.shape[1]]

    # =========================
    # 🔢 NUMERIC CLEAN
    # =========================
    num_cols = [
        "Opening Balance","Sales Value","Returns Value",
        "Tasweyat Madinah (Credit)","Total Collection",
        "Madfoaat","Tasweyat Madinah (Debit)",
        "End Balance","Motalbet El Fatrah"
    ]

    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    # =========================
    # 🧠 REP LOGIC (SAFE - NO ASSIGNMENT CRASH)
    # =========================

    mask = df["Sales Value"].astype(str).str.contains("مندوب المبيعات", na=False)

    rep_code_series = pd.Series(np.nan, index=df.index)
    rep_name_series = pd.Series("", index=df.index)

    rep_code_series.loc[mask] = df.loc[mask, "Returns Value"]
    rep_name_series.loc[mask] = df.loc[mask, "Tasweyat Madinah (Credit)"].astype(str)

    # 🔽 fill down BEFORE attaching
    rep_code_series = rep_code_series.ffill()
    rep_name_series = rep_name_series.ffill()

    # attach safely
    df["Rep Code"] = rep_code_series
    df["Rep Name"] = rep_name_series

    # =========================
    # 🧹 REMOVE MARKER ROWS
    # =========================
    df = df[~mask].copy()

    return df


# =========================
# 📥 RUN
# =========================
df = load_client_haraka()

# =========================
# 📊 UI
# =========================
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
