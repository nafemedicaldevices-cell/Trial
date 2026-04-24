import streamlit as st
import pandas as pd
import numpy as np
import os

st.set_page_config(page_title="Client Harakah", layout="wide")
st.title("👤 Client Harakah Dashboard")

# =========================
# 📂 LOAD DATA
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
    # 🧠 REP EXTRACTION (FIXED)
    # =========================

    # مهم جدًا
    df["Sales Value"] = df["Sales Value"].astype(str)

    df["Rep Code"] = np.nan
    df["Rep Name"] = np.nan

    # 🔍 الماركَر الحقيقي
    mask = df["Sales Value"].str.contains("مندوب المبيعات", na=False)

    # 📌 استخراج
    df.loc[mask, "Rep Code"] = df.loc[mask, "Returns Value"]
    df.loc[mask, "Rep Name"] = df.loc[mask, "Tasweyat Madinah (Credit)"]

    # 🔽 Fill Down
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
# 📥 RUN
# =========================
df = load_client_haraka()

# =========================
# 📊 DISPLAY
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
