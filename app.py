import streamlit as st
import pandas as pd
import data_pipeline as dp

# =========================
# 🎨 PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Sales Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📊 Sales Performance Dashboard")

# =========================
# 📂 LOAD & BUILD
# =========================
@st.cache_data
def get_data():
    data   = dp.load_data()
    # fix Rep file name
    data["target_rep"] = pd.read_excel("Rep.xlsx")
    master = dp.build_all(data)
    return master

with st.spinner("جاري تحميل البيانات..."):
    master = get_data()

sales       = master["sales"]
targets     = master["targets"]
overdue     = master["overdue"]
opening     = master["opening"]
achievement = master["achievement"]

# =========================
# 🔎 SIDEBAR FILTERS
# =========================
st.sidebar.header("🔎 فلتر")

# collect all unique codes from sales raw
raw = sales["raw"]

manager_list  = sorted(raw["Manager Code"].dropna().unique().tolist())
area_list     = sorted(raw["Area Code"].dropna().unique().tolist())
rep_list      = sorted(raw["Rep Code"].dropna().unique().tolist())

sel_manager  = st.sidebar.selectbox("Manager",  ["الكل"] + [str(x) for x in manager_list])
sel_area     = st.sidebar.selectbox("Area",     ["الكل"] + [str(x) for x in area_list])
sel_rep      = st.sidebar.selectbox("Rep",      ["الكل"] + [str(x) for x in rep_list])

def filter_df(df, id_col):
    """Apply sidebar filters to any grouped df that has the relevant column."""
    d = df.copy()
    if sel_manager != "الكل" and "Manager Code" in d.columns:
        d = d[d["Manager Code"].astype(str) == sel_manager]
    if sel_area != "الكل" and "Area Code" in d.columns:
        d = d[d["Area Code"].astype(str) == sel_area]
    if sel_rep != "الكل" and "Rep Code" in d.columns:
        d = d[d["Rep Code"].astype(str) == sel_rep]
    return d

# =========================
# 📑 TABS
# =========================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💰 Sales KPI",
    "🎯 Target KPI",
    "🏆 Achievement",
    "📬 Overdue",
    "🗂️ Opening",
])

# ─────────────────────────────────────────────
# TAB 1 — SALES KPI
# ─────────────────────────────────────────────
with tab1:
    st.subheader("💰 Sales KPI")

    level = st.radio("مستوى", ["Rep", "Manager", "Area", "Supervisor"], horizontal=True, key="sales_level")

    level_map = {
        "Rep":        ("rep_value",        "Rep Code"),
        "Manager":    ("manager_value",    "Manager Code"),
        "Area":       ("area_value",       "Area Code"),
        "Supervisor": ("supervisor_value", "Supervisor Code"),
    }
    key, id_col = level_map[level]
    df = filter_df(sales[key], id_col)

    # KPI cards
    total_sales   = df["Total Sales Value"].sum()
    total_returns = df["Returns Value"].sum()
    net_sales     = df["Sales After Returns"].sum()

    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي المبيعات",  f"{total_sales:,.0f}")
    c2.metric("إجمالي المرتجعات", f"{total_returns:,.0f}")
    c3.metric("صافي المبيعات",    f"{net_sales:,.0f}")

    st.dataframe(df, use_container_width=True, hide_index=True)

    # products breakdown
    with st.expander("📦 تفاصيل المنتجات"):
        prod_key = level.lower() + "_products"
        prod_df  = filter_df(sales[prod_key], id_col)
        st.dataframe(prod_df, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# TAB 2 — TARGET KPI
# ─────────────────────────────────────────────
with tab2:
    st.subheader("🎯 Target KPI")

    level_t = st.radio(
        "مستوى", ["rep", "manager", "area", "supervisor", "evak"],
        horizontal=True, key="target_level",
        format_func=lambda x: x.capitalize()
    )

    id_map_t = {
        "rep": "Rep Code", "manager": "Manager Code",
        "area": "Area Code", "supervisor": "Supervisor Code", "evak": "Evak Code",
    }
    id_col_t = id_map_t[level_t]

    val_tbl = targets[level_t]["value_table"]
    st.markdown("#### القيمة")
    st.dataframe(val_tbl, use_container_width=True, hide_index=True)

    with st.expander("📦 تفاصيل المنتجات"):
        period = st.selectbox("الفترة", ["Full Year", "Month", "Quarter", "YTD"], key="tgt_period")
        period_key = {
            "Full Year": "products_full",
            "Month":     "products_month",
            "Quarter":   "products_quarter",
            "YTD":       "products_ytd",
        }[period]
        st.dataframe(targets[level_t][period_key], use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# TAB 3 — ACHIEVEMENT
# ─────────────────────────────────────────────
with tab3:
    st.subheader("🏆 Achievement % (Actual ÷ Target)")

    level_a = st.radio(
        "مستوى", ["rep", "manager", "area", "supervisor"],
        horizontal=True, key="ach_level",
        format_func=lambda x: x.capitalize()
    )

    ach_df = achievement[level_a]

    if ach_df.empty:
        st.warning("مفيش بيانات للمستوى ده.")
    else:
        # color-code achievement %
        def color_pct(val):
            if pd.isna(val):
                return ""
            if val >= 100:
                return "background-color: #d4edda"
            elif val >= 80:
                return "background-color: #fff3cd"
            else:
                return "background-color: #f8d7da"

        pct_cols = [c for c in ach_df.columns if c.startswith("Ach%")]

        styled = ach_df.style.applymap(color_pct, subset=pct_cols)
        st.dataframe(styled, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# TAB 4 — OVERDUE
# ─────────────────────────────────────────────
with tab4:
    st.subheader("📬 Overdue KPI (120 يوم+)")

    level_o = st.radio(
        "مستوى", ["Rep", "Manager", "Area", "Supervisor"],
        horizontal=True, key="ov_level"
    )

    sum_key = level_o.lower() + "_summary"
    det_key = level_o.lower() + "_details"

    ov_sum = overdue[sum_key]
    ov_det = overdue[det_key]

    total_overdue = ov_sum["Overdue"].sum()
    st.metric("إجمالي المتأخر (120d+)", f"{total_overdue:,.0f}")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**ملخص**")
        st.dataframe(ov_sum, use_container_width=True, hide_index=True)
    with col2:
        st.markdown("**تفاصيل العملاء**")
        st.dataframe(ov_det, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# TAB 5 — OPENING
# ─────────────────────────────────────────────
with tab5:
    st.subheader("🗂️ Opening KPI")

    level_op = st.radio(
        "مستوى", ["Rep", "Manager", "Area", "Supervisor"],
        horizontal=True, key="op_level"
    )

    op_key = level_op.lower() + "_summary"
    op_df  = opening[op_key]

    total_collection  = op_df["Total Collection"].sum()  if "Total Collection"  in op_df.columns else 0
    total_end_balance = op_df["End Balance"].sum()        if "End Balance"        in op_df.columns else 0
    total_extra_disc  = op_df["Extra Discounts"].sum()    if "Extra Discounts"    in op_df.columns else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي التحصيل",       f"{total_collection:,.0f}")
    c2.metric("الرصيد الآخر",          f"{total_end_balance:,.0f}")
    c3.metric("خصومات إضافية",         f"{total_extra_disc:,.0f}")

    st.dataframe(op_df, use_container_width=True, hide_index=True)
