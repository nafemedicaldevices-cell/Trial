import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")

st.title("🔥 Sales Dashboard")

# ==============================
# 🧪 DEBUG: Show errors
# ==============================
def show_df_info(name, df):
    st.subheader(f"{name} Info")
    st.write("Shape:", df.shape)
    st.write("Columns:", list(df.columns))
    st.dataframe(df.head())


# ==============================
# 🧹 Clean Key
# ==============================
def clean_key(df, key="Rep Code"):
    df[key] = pd.to_numeric(df[key], errors="coerce")
    df = df.dropna(subset=[key])
    df[key] = df[key].astype("int64")
    return df


# ==============================
# 🎯 TARGET
# ==============================
def build_target_pipeline(rep):
    df = rep["value_table"].copy()

    df = df.rename(columns={
        "Full Year 🏆": "Target",
        "Month 📅": "Target Month",
        "Quarter 📊": "Target Quarter",
        "YTD 📈": "Target YTD"
    })

    df = clean_key(df)

    df = df.groupby("Rep Code", as_index=False).sum()

    return df


# ==============================
# 💰 SALES
# ==============================
def build_sales_pipeline(sales):
    df = sales.copy()

    # 🧪 تأكد العمود موجود
    if "Date" not in df.columns:
        st.error("❌ Column 'Date' مش موجود في sales")
        st.stop()

    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    df['Month'] = df['Date'].dt.month
    df['Year'] = df['Date'].dt.year
    df['Quarter'] = df['Date'].dt.quarter

    today = pd.Timestamp.today()
    current_month = today.month
    current_year = today.year
    current_quarter = (current_month - 1) // 3 + 1

    # KPIs
    df['Net After Discounts'] = (
        df['Sales After Returns'] - df['Invoice Discounts']
    )

    df = clean_key(df)

    # Filters
    full = df.copy()
    month = df[(df['Month'] == current_month) & (df['Year'] == current_year)]
    quarter = df[(df['Quarter'] <= current_quarter) & (df['Year'] == current_year)]
    ytd = df[(df['Month'] <= current_month) & (df['Year'] == current_year)]

    def group(x):
        return x.groupby("Rep Code", as_index=False)[
            ["Total Sales Value","Returns Value","Sales After Returns","Invoice Discounts","Net After Discounts"]
        ].sum()

    full_g = group(full)
    month_g = group(month)
    quarter_g = group(quarter)
    ytd_g = group(ytd)

    df_final = full_g.merge(month_g, on="Rep Code", how="left", suffixes=("", "_Month"))
    df_final = df_final.merge(quarter_g, on="Rep Code", how="left", suffixes=("", "_Quarter"))
    df_final = df_final.merge(ytd_g, on="Rep Code", how="left", suffixes=("", "_YTD"))

    return df_final.fillna(0)


# ==============================
# 🏦 OPENING
# ==============================
def build_opening_pipeline(opening):
    df = opening.copy()

    df = clean_key(df)

    df['Total Collection'] = (
        df['Cash Collection'] + df['Collection Checks']
    )

    df = df.groupby("Rep Code", as_index=False)[
        ["Opening Balance","Total Collection","Extra Discounts","End Balance"]
    ].sum()

    return df


# ==============================
# 📉 OVERDUE
# ==============================
def build_overdue_pipeline(overdue):
    df = overdue.copy()

    df = clean_key(df)

    df["Overdue Value"] = (
        df["120 Days"] + df["More Than 120 Days"]
    )

    df = df.groupby("Rep Code", as_index=False)[
        ["Overdue Value"]
    ].sum()

    return df


# ==============================
# 🔗 MASTER
# ==============================
def build_master(target, sales, overdue, opening):

    final = target.merge(sales, on="Rep Code", how="outer")
    final = final.merge(overdue, on="Rep Code", how="outer")
    final = final.merge(opening, on="Rep Code", how="outer")

    final = final.fillna(0)

    # KPIs
    if "Target" in final.columns:
        final["Achievement %"] = final["Total Sales Value"] / final["Target"]

    if "Sales After Returns" in final.columns:
        final["Collection Efficiency"] = (
            final["Total Collection"] / final["Sales After Returns"]
        )

        final["Risk %"] = (
            final["Overdue Value"] / final["Sales After Returns"]
        )

    return final


# ==============================
# 📥 LOAD DATA (عدّل هنا)
# ==============================

# ❗ استبدل دي بداتا حقيقية
# مثال:
# rep = {"value_table": pd.read_excel("target.xlsx")}
# sales = pd.read_excel("sales.xlsx")
# opening = pd.read_excel("opening.xlsx")
# overdue = pd.read_excel("overdue.xlsx")

rep = {"value_table": pd.DataFrame()}
sales = pd.DataFrame()
opening = pd.DataFrame()
overdue = pd.DataFrame()


# ==============================
# 🧪 DEBUG VIEW
# ==============================
if st.checkbox("Show Raw Data"):
    show_df_info("Target", rep["value_table"])
    show_df_info("Sales", sales)
    show_df_info("Opening", opening)
    show_df_info("Overdue", overdue)


# ==============================
# ▶️ RUN
# ==============================
try:
    target_rep = build_target_pipeline(rep)
    sales_rep = build_sales_pipeline(sales)
    opening_rep = build_opening_pipeline(opening)
    overdue_rep = build_overdue_pipeline(overdue)

    final = build_master(target_rep, sales_rep, overdue_rep, opening_rep)

    st.success("✅ Data Loaded Successfully")

    st.subheader("📊 Final Table")
    st.write("Shape:", final.shape)
    st.dataframe(final, use_container_width=True)

except Exception as e:
    st.error("❌ حصل Error")
    st.write(e)
