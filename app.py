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
# 🎯 TARGETS
# =========================
rep_target = dp.build_target_pipeline(data["target_rep"], "Rep Code")
manager_target = dp.build_target_pipeline(data["target_manager"], "Manager Code")
area_target = dp.build_target_pipeline(data["target_area"], "Area Code")
supervisor_target = dp.build_target_pipeline(data["target_supervisor"], "Supervisor Code")


# =========================
# 💰 SALES
# =========================
sales = dp.build_sales_pipeline(
    data["sales"],
    data["mapping"],
    data["codes"]
)

groups = dp.build_groups(sales)


# =========================
# 🔗 MERGE SAFE
# =========================
def safe_merge(left, right, key):

    if key in left.columns and key in right.columns:
        return left.merge(right, on=key, how="left")

    return left


rep = safe_merge(groups["rep"], rep_target, "Rep Code")
manager = safe_merge(groups["manager"], manager_target, "Manager Code")
area = safe_merge(groups["area"], area_target, "Area Code")
supervisor = safe_merge(groups["supervisor"], supervisor_target, "Supervisor Code")


# =========================
# 📊 ACHIEVEMENT %
# =========================
def achievement(df, target_col):

    if target_col not in df.columns:
        df[target_col] = 0

    df[target_col] = df[target_col].fillna(0)

    df["Achievement %"] = 0

    mask = df[target_col] > 0

    df.loc[mask, "Achievement %"] = (
        df.loc[mask, "Total Sales Value"] / df.loc[mask, target_col]
    ) * 100

    return df


rep = achievement(rep, "Target Value")
manager = achievement(manager, "Target Value")
area = achievement(area, "Target Value")
supervisor = achievement(supervisor, "Target Value")


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
