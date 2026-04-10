import streamlit as st
import data_pipeline as dp

st.set_page_config(layout="wide")
st.title("📊 Sales vs Target Dashboard")


# =========================
# LOAD
# =========================
data = dp.load_data()

sales = dp.build_sales_pipeline(
    data["sales"],
    data["mapping"],
    data["codes"]
)

rep_target = dp.build_target_pipeline(data["target_rep"], "Rep Code")
manager_target = dp.build_target_pipeline(data["target_manager"], "Manager Code")
area_target = dp.build_target_pipeline(data["target_area"], "Area Code")
supervisor_target = dp.build_target_pipeline(data["target_supervisor"], "Supervisor Code")


# =========================
# SAFE GROUP SALES
# =========================
def group_sales(df, key):
    if key not in df.columns:
        return df.iloc[0:0]

    return df.groupby(key, as_index=False).agg({
        "Total Sales Value": "sum",
        "Returns Value": "sum",
        "Sales After Returns": "sum",
        "Invoice Discounts": "sum"
    })


# =========================
# SAFE MERGE
# =========================
def safe_merge(left, right, key):

    if key not in left.columns:
        st.warning(f"Missing {key} in sales")
        return left.iloc[0:0]

    if key not in right.columns:
        st.warning(f"Missing {key} in target")
        return left.iloc[0:0]

    return left.merge(right, on=key, how="left")


# =========================
# BUILD KPI LEVEL
# =========================
def build_level(target_df, key):

    sales_grp = group_sales(sales, key)

    merged = safe_merge(sales_grp, target_df, key)

    if "Target Value" not in merged.columns:
        merged["Target Value"] = 0

    merged["Achievement %"] = 0

    mask = merged["Target Value"] > 0

    merged.loc[mask, "Achievement %"] = (
        merged.loc[mask, "Total Sales Value"] /
        merged.loc[mask, "Target Value"]
    ) * 100

    return merged


# =========================
# RESULTS
# =========================
rep = build_level(rep_target, "Rep Code")
manager = build_level(manager_target, "Manager Code")
area = build_level(area_target, "Area Code")
supervisor = build_level(supervisor_target, "Supervisor Code")


# =========================
# DASHBOARD
# =========================
st.header("👨‍💼 Rep")
st.dataframe(rep, use_container_width=True)

st.header("🏢 Manager")
st.dataframe(manager, use_container_width=True)

st.header("🌍 Area")
st.dataframe(area, use_container_width=True)

st.header("🧑‍💼 Supervisor")
st.dataframe(supervisor, use_container_width=True)
