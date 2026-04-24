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
    # 1️⃣ READ RAW (NO HEADER)
    # =========================
    df = pd.read_excel(file_path, header=None)

    # =========================
    # 2️⃣ CLEAN FIRST COLUMN (MAIN FILTER)
    # =========================
    first_col = df.columns[0]

    df[first_col] = df[first_col].astype(str)

    df = df[
        (df[first_col].str.strip() != "") &          # remove empty
        (~df[first_col].str.contains("كود العميل", na=False)) &  # remove headers repeat
        (~df[first_col].str.contains("كود الفرع", na=False)) &   # remove metadata
        (~df[first_col].str.contains("اجمال", na=False))         # remove totals
    ].copy()

    df = df.reset_index(drop=True)

    # =========================
    # 3️⃣ FIND REP ROW BEFORE CLEANING TYPES
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
    # 4️⃣ REMOVE REP ROW
    # =========================
    df = df[~rep_mask].reset_index(drop=True)

    # =========================
    # 5️⃣ SET PROPER HEADERS
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
    # 6️⃣ NUMERIC CLEAN
    # =========================
    num_cols = [
        "Opening Balance","Sales Value","Returns Value",
        "Tasweyat Madinah (Credit)","Total Collection",
        "Madfoaat","Tasweyat Madinah (Debit)",
        "End Balance","Motalbet El Fatrah"
    ]

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
