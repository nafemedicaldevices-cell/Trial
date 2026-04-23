import streamlit as st
from cleaning import load_data

# =========================
# 📊 TITLE
# =========================
st.title("📊 Rep Harakah - Clean Data System")

# =========================
# 📥 LOAD DATA
# =========================
df = load_data()

# =========================
# 📊 METRICS
# =========================
c1, c2, c3 = st.columns(3)

c1.metric("Rows", len(df))
c2.metric("Sales Value", f"{df['Sales Value'].sum():,.0f}")
c3.metric("Returns Value", f"{df['Returns Value'].sum():,.0f}")

# =========================
# 📊 FILTER
# =========================
rep = st.selectbox("Select Rep", ["All"] + df["Rep Name"].dropna().unique().tolist())

if rep != "All":
    df = df[df["Rep Name"] == rep]

# =========================
# 📊 OUTPUT
# =========================
st.dataframe(df, use_container_width=True)
