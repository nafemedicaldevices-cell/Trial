# =========================
# 🔍 DATA VALIDATION LAYER
# =========================
st.header("🔍 Data Validation & Debug")

# Toggle
show_debug = st.checkbox("Show Debug Data")

if show_debug:

    # =========================
    # 📦 SALES CHECK
    # =========================
    st.subheader("💰 Sales Check")

    st.write("🔴 Raw Sales")
    st.dataframe(data["sales"].head(10))

    st.write("🟢 Clean Sales")
    st.dataframe(sales_clean.head(10))

    st.write("📊 Data Types")
    st.write(sales_clean.dtypes)

    st.write("❗ Missing Values")
    st.write(sales_clean.isna().sum())

    st.write("🔢 Unique Rep Codes")
    st.write(sales_clean["Rep Code"].nunique())

    st.write("🚨 Null Rep Codes")
    st.write(sales_clean["Rep Code"].isna().sum())


    # =========================
    # 📦 OPENING CHECK
    # =========================
    st.subheader("📦 Opening Check")

    st.write("🔴 Raw Opening")
    st.dataframe(data["opening"].head(10))

    st.write("🟢 Clean Opening")
    st.dataframe(opening_clean.head(10))

    st.write("📊 Data Types")
    st.write(opening_clean.dtypes)

    st.write("❗ Missing Values")
    st.write(opening_clean.isna().sum())

    st.write("🚨 Null Rep Codes")
    st.write(opening_clean["Rep Code"].isna().sum())


    # =========================
    # ⏳ OVERDUE CHECK
    # =========================
    st.subheader("⏳ Overdue Check")

    st.write("🔴 Raw Overdue")
    st.dataframe(data["overdue"].head(10))

    st.write("🟢 Clean Overdue")
    st.dataframe(overdue_clean.head(10))

    st.write("📊 Data Types")
    st.write(overdue_clean.dtypes)

    st.write("❗ Missing Values")
    st.write(overdue_clean.isna().sum())

    st.write("🚨 Null Rep Codes")
    st.write(overdue_clean["Rep Code"].isna().sum())
