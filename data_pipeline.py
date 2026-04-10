import streamlit as st
import data_pipeline as dp


# =========================
# 🎨 UI
# =========================
st.set_page_config(layout="wide")
st.title("📊 Sales vs Target Dashboard")


# =========================
# 📥 LOAD DATA
# =========================
data = dp.load_data()


# =========================
# 💰 SALES
# =========================
sales = dp.build_sales_pipeline(
    data["sales"],
    data["mapping"],
    data["codes"]
)


# =========================
# 🎯 TARGETS
# =========================
rep_target = dp.build_target_pipeline(data["target_rep"], "Rep Code")
manager_target = dp.build_target_pipeline(data["target_manager"], "Manager Code")
area_target = dp.build_target_pipeline(data["target_area"], "Area Code")
supervisor_target = dp.build_target_pipeline(data["target_supervisor"], "Supervisor Code")


# =========================
# 📊 SALES GROUPING
# =========================
rep_sales = sales.groupby("Rep Code", as_index=False).agg({
    "Total Sales Value": "sum",
    "Returns Value": "sum",
    "Sales After Returns": "sum"
})


manager_sales = sales.groupby("Manager Code", as_index=False).agg({
    "Total Sales Value": "sum",
    "Returns Value": "sum",
    "Sales After Returns": "sum"
})


area_sales = sales.groupby("Area Code", as_index=False).agg({
    "Total Sales Value": "sum",
    "Returns Value": "sum",
    "Sales After Returns": "sum"
})


supervisor_sales = sales.groupby("Supervisor Code", as_index=False).agg({
    "Total Sales Value": "sum",
    "Returns Value": "sum",
    "Sales After Returns": "sum"
})


# =========================
# 🔗 MERGE TARGET
# =========================
rep = rep_sales.merge(rep_target, on="Rep Code", how="left")
manager = manager_sales.merge(manager_target, on="Manager Code", how="left")
area = area_sales.merge(area_target, on="Area Code", how="left")
supervisor = supervisor_sales.merge(supervisor_target, on="Supervisor Code", how="left")


# =========================
# 📊 ACHIEVEMENT %
# =========================
def achievement(df):

    if "Target Value" not in df.columns:
        df["Target Value"] = 0

    df["Target Value"] = df["Target Value"].fillna(0)

    df["Achievement %"] = 0

    mask = df["Target Value"] > 0

    df.loc[mask, "Achievement %"] = (
        df.loc[mask, "Total Sales Value"] / df.loc[mask, "Target Value"]
    ) * 100

    return df


rep = achievement(rep)
manager = achievement(manager)
area = achievement(area)
supervisor = achievement(supervisor)


# =========================
# 📊 OUTPUT
# =========================
st.header("🔥 SALES VS TARGET")

st.subheader("👨‍💼 Rep")
st.dataframe(rep, use_container_width=True)

st.subheader("🏢 Manager")
st.dataframe(manager, use_container_width=True)

st.subheader("🌍 Area")
st.dataframe(area, use_container_width=True)

st.subheader("🧑‍💼 Supervisor")
st.dataframe(supervisor, use_container_width=True)
