import streamlit as st
import pandas as pd
import numpy as np

# =========================
# 📌 LOAD DATA (مفترض إنك معرفهم من ملفاتك)
# =========================
# دول لازم يكونوا راجعين من functions بتاعتك
# مثال:
# targets_dict = load_targets()
# sales_dict = load_sales()
# codes_df = load_codes()

# =========================
# 🧠 SAFETY CHECK
# =========================
if "targets_dict" not in globals():
    st.error("targets_dict not loaded")
    st.stop()

if "sales_dict" not in globals():
    st.error("sales_dict not loaded")
    st.stop()

if "codes_df" not in globals():
    st.error("codes_df not loaded")
    st.stop()

# =========================
# 🎛️ UI
# =========================
st.title("📊 Sales vs Target Dashboard")

# اختيار Target sheet
target_sheet = st.selectbox(
    "Select Target Sheet",
    list(targets_dict.keys())
)

target_df = targets_dict[target_sheet]

# اختيار Code
selected_code = st.selectbox(
    "Select Rep Code",
    codes_df["Rep Code"].dropna().unique()
)

# اختيار Sales sheet (لو عندك أكتر من شيت)
sales_sheet = st.selectbox(
    "Select Sales Sheet",
    list(sales_dict.keys())
)

sales_df = sales_dict[sales_sheet]

# =========================
# 🔗 FILTER TARGET
# =========================
target_df = target_df.merge(
    codes_df,
    on="Code",
    how="left"
)

target_df = target_df[
    target_df["Rep Code"].astype(str).str.strip()
    == str(selected_code).strip()
]

# =========================
# 🔗 FILTER SALES
# =========================
sales_df = sales_df[
    sales_df["Rep Code"].astype(str).str.strip()
    == str(selected_code).strip()
]

# =========================
# 📊 AGG SALES
# =========================
sales_agg = sales_df.groupby(
    "Product Name",
    as_index=False
).agg({
    "Sales Unit": "sum",
    "Sales Value": "sum"
})

# =========================
# 📊 AGG TARGET
# =========================
target_agg = target_df.groupby(
    "Old Product Name",
    as_index=False
).agg({
    "Target (Unit)": "sum",
    "Target (Value)": "sum"
})

# =========================
# 🔗 MERGE
# =========================
df = target_agg.merge(
    sales_agg,
    left_on="Old Product Name",
    right_on="Product Name",
    how="left"
)

df = df.fillna(0)

# =========================
# 📈 ACHIEVEMENT %
# =========================
df["Achievement Unit %"] = np.where(
    df["Target (Unit)"] > 0,
    df["Sales Unit"] / df["Target (Unit)"],
    0
)

df["Achievement Value %"] = np.where(
    df["Target (Value)"] > 0,
    df["Sales Value"] / df["Target (Value)"],
    0
)

# =========================
# 🧾 FINAL TABLE
# =========================
final_df = df[[
    "Old Product Name",
    "Target (Unit)",
    "Sales Unit",
    "Achievement Unit %",
    "Target (Value)",
    "Sales Value",
    "Achievement Value %"
]]

final_df.columns = [
    "Product Name",
    "Target Unit",
    "Sales Unit",
    "Achievement Unit %",
    "Target Value",
    "Sales Value",
    "Achievement Value %"
]

# =========================
# 📊 DISPLAY
# =========================
st.subheader("📌 Performance Table")

st.dataframe(
    final_df,
    use_container_width=True
)

# =========================
# 📊 DEBUG (مهم جدًا)
# =========================
with st.expander("🔍 Debug Info"):
    st.write("Target rows:", len(target_df))
    st.write("Sales rows:", len(sales_df))
    st.write("Merged rows:", len(final_df))
