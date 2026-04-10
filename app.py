import streamlit as st
import data_pipeline as dp


# =========================
# 🎨 UI
# =========================
st.set_page_config(layout="wide")
st.title("📊 Sales vs Target Dashboard")


# =========================
# 📥 LOAD
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
# 📊 GROUP SALES
# =========================
rep_sales = sales.groupby("rep_code", as_index=False).agg({
    "total_sales_value": "sum",
    "returns_value": "sum",
    "sales_after_returns": "sum"
})

manager_sales = sales.groupby("manager_code", as_index=False).agg({
    "total_sales_value": "sum",
    "returns_value": "sum",
    "sales_after_returns": "sum"
})

area_sales = sales.groupby("area_code", as_index=False).agg({
    "total_sales_value": "sum",
    "returns_value": "sum",
    "sales_after_returns": "sum"
})

supervisor_sales = sales.groupby("supervisor_code", as_index=False).agg({
    "total_sales_value": "sum",
    "returns_value": "sum",
    "sales_after_returns": "sum"
})


# =========================
# 🔗 MERGE
# =========================
rep = rep_sales.merge(rep_target, on="rep_code", how="left")
manager = manager_sales.merge(manager_target, on="manager_code", how="left")
area = area_sales.merge(area_target, on="area_code", how="left")
supervisor = supervisor_sales.merge(supervisor_target, on="supervisor_code", how="left")


# =========================
# 📊 ACHIEVEMENT %
# =========================
def achievement(df):

    if "target_value" not in df.columns:
        df["target_value"] = 0

    df["target_value"] = df["target_value"].fillna(0)

    df["achievement_%"] = 0

    mask = df["target_value"] > 0

    df.loc[mask, "achievement_%"] = (
        df.loc[mask, "total_sales_value"] / df.loc[mask, "target_value"]
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
