"""
Sales Performance Dashboard — Streamlit App
Run: streamlit run dashboard_app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  GLOBAL STYLE
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Cairo', sans-serif !important; }

/* Hide default streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1rem 2rem 2rem; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #1B2A4A;
    color: white;
}
section[data-testid="stSidebar"] * { color: white !important; }
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stRadio label { color: #BDD7EE !important; font-size: 12px; }

/* Metric cards */
div[data-testid="metric-container"] {
    background: white;
    border: 1px solid #E8EDF3;
    border-radius: 12px;
    padding: 12px 16px;
    border-left: 4px solid #2E75B6;
}
div[data-testid="metric-container"] > div { gap: 2px; }
div[data-testid="metric-container"] label { font-size: 11px !important; color: #6B7A8D !important; }
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    font-size: 22px !important; font-weight: 700 !important; color: #1B2A4A !important;
}
div[data-testid="metric-container"] div[data-testid="stMetricDelta"] {
    font-size: 11px !important;
}

/* Section headers */
.sec-header {
    display: flex; align-items: center; gap: 10px;
    margin: 1.5rem 0 0.8rem;
    padding-bottom: 8px;
    border-bottom: 2px solid #E8EDF3;
}
.sec-icon {
    width: 32px; height: 32px; border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px;
}
.sec-title { font-size: 15px; font-weight: 700; color: #1B2A4A; }
.sec-subtitle { font-size: 11px; color: #8A9BB0; margin-left: auto; }

/* Top banner */
.top-banner {
    background: linear-gradient(135deg, #1B2A4A 0%, #2E75B6 100%);
    border-radius: 14px;
    padding: 18px 28px;
    margin-bottom: 20px;
    display: flex; align-items: center; justify-content: space-between;
}
.top-banner h1 { color: white; font-size: 22px; font-weight: 700; margin: 0; }
.top-banner p  { color: #BDD7EE; font-size: 12px; margin: 4px 0 0; }

/* Achievement badge */
.badge-hit  { background:#EAF3DE; color:#3B6D11; padding:3px 10px; border-radius:20px; font-size:11px; font-weight:600; }
.badge-miss { background:#FCEBEB; color:#A32D2D; padding:3px 10px; border-radius:20px; font-size:11px; font-weight:600; }
.badge-ok   { background:#E6F1FB; color:#185FA5; padding:3px 10px; border-radius:20px; font-size:11px; font-weight:600; }

/* Plotly chart container */
.stPlotlyChart { border-radius: 12px; overflow: hidden; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 4px; background: #F4F6FB; border-radius: 10px; padding: 4px; }
.stTabs [data-baseweb="tab"] {
    border-radius: 8px; padding: 6px 18px; font-size: 13px;
    font-weight: 500; color: #6B7A8D; background: transparent; border: none;
}
.stTabs [aria-selected="true"] { background: white !important; color: #1B2A4A !important; font-weight: 700 !important; }

/* Dataframe */
.stDataFrame { border-radius: 10px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  COLOURS
# ─────────────────────────────────────────────
C_BLUE   = "#2E75B6"
C_TEAL   = "#00B0F0"
C_GREEN  = "#70AD47"
C_ORANGE = "#ED7D31"
C_RED    = "#E24B4A"
C_PURPLE = "#7F77DD"
C_NAVY   = "#1B2A4A"
C_LGRAY  = "#F4F6FB"

PALETTE = [C_BLUE, C_TEAL, C_GREEN, C_ORANGE, C_PURPLE, C_RED]

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def fmt_k(v):
    if v >= 1_000_000: return f"{v/1_000_000:.1f}M"
    if v >= 1_000:     return f"{v/1_000:.0f}K"
    return f"{v:.0f}"

def pct_color(p):
    if p >= 100: return C_GREEN
    if p >= 85:  return C_ORANGE
    return C_RED

def make_gauge(value, max_val, color, title):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(value, 1),
        number={"suffix": "%", "font": {"size": 28, "color": C_NAVY, "family": "Cairo"}},
        title={"text": title, "font": {"size": 12, "color": "#6B7A8D", "family": "Cairo"}},
        gauge={
            "axis": {"range": [0, 120], "tickcolor": "#ccc", "tickfont": {"size": 9}},
            "bar":  {"color": color, "thickness": 0.35},
            "bgcolor": "#F4F6FB",
            "borderwidth": 0,
            "steps": [
                {"range": [0,   85],  "color": "#FCEBEB"},
                {"range": [85,  100], "color": "#FFF3E0"},
                {"range": [100, 120], "color": "#EAF3DE"},
            ],
            "threshold": {
                "line": {"color": C_NAVY, "width": 2},
                "thickness": 0.75,
                "value": 100
            }
        }
    ))
    fig.update_layout(
        height=200, margin=dict(t=40, b=10, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig

def make_progress_bar(pct, color):
    clamped = min(pct, 100)
    fig = go.Figure(go.Bar(
        x=[clamped], y=[""], orientation="h",
        marker_color=color, width=0.4
    ))
    fig.add_shape(type="line", x0=100, x1=100, y0=-0.5, y1=0.5,
                  line=dict(color=C_NAVY, width=2, dash="dot"))
    fig.update_layout(
        height=40, margin=dict(t=0, b=0, l=0, r=0),
        xaxis=dict(range=[0, 120], showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(showticklabels=False, showgrid=False),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#F4F6FB",
        bargap=0
    )
    return fig

# ─────────────────────────────────────────────
#  DATA LOADING
# ─────────────────────────────────────────────
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x: '%.0f' % x)

current_month = pd.Timestamp.today().month

@st.cache_data(show_spinner="جاري تحميل البيانات...")
def load_all():
    sales_raw         = pd.read_excel("Sales.xlsx")
    overdue_raw       = pd.read_excel("Overdue.xlsx")
    extra_disc_raw    = pd.read_excel("Extradiscounts.xlsx")
    opening_raw       = pd.read_excel("Opening.xlsx")
    opening_detail_raw= pd.read_excel("Opening Detail.xlsx")
    target_manager_raw= pd.read_excel("Target Manager.xlsx")
    target_area_raw   = pd.read_excel("Target Area.xlsx")
    target_rep_raw    = pd.read_excel("Target Rep.xlsx")
    mapping_raw       = pd.read_excel("Mapping.xlsx")
    codes_raw         = pd.read_excel("Code.xlsx")
    return (sales_raw, overdue_raw, extra_disc_raw, opening_raw,
            opening_detail_raw, target_manager_raw, target_area_raw,
            target_rep_raw, mapping_raw, codes_raw)


def safe_group(df, group_cols, sum_cols):
    group_cols = [c for c in group_cols if c in df.columns]
    sum_cols   = [c for c in sum_cols   if c in df.columns]
    if not group_cols:
        return pd.DataFrame(columns=sum_cols)
    return df.groupby(group_cols, as_index=False)[sum_cols].sum()


@st.cache_data(show_spinner="جاري معالجة البيانات...")
def process_all():
    (sales_raw, overdue_raw, extra_disc_raw, opening_raw,
     opening_detail_raw, target_manager_raw, target_area_raw,
     target_rep_raw, mapping_raw, codes_raw) = load_all()

    mapping = mapping_raw.copy()
    codes   = codes_raw.copy()

    # ── TARGET PIPELINE ──────────────────────────────────────
    def build_target_pipeline(df_raw, id_name):
        df = df_raw.copy()
        df.columns = df.columns.str.strip().str.replace(r'\s+', ' ', regex=True)
        fixed_cols   = ["Year", "Product Code", "Old Product Name", "Sales Price"]
        dynamic_cols = [c for c in df.columns if c not in fixed_cols]
        df = df.melt(id_vars=fixed_cols, value_vars=dynamic_cols,
                     var_name=id_name, value_name="Target (Unit)")
        df[id_name] = (df[id_name].astype(str)
                       .str.replace(r'[^0-9]', '', regex=True))
        df[id_name] = pd.to_numeric(df[id_name], errors='coerce').astype('Int64')
        for col in ["Target (Unit)", "Sales Price", "Product Code"]:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(r'[^0-9.]', '', regex=True),
                errors='coerce'
            ).fillna(0)
        mc = mapping.copy()
        mc["Product Code"] = pd.to_numeric(
            mc["Product Code"].astype(str).str.replace(r'[^0-9.]', '', regex=True),
            errors='coerce'
        ).fillna(0).astype(int)
        mc = mc.drop_duplicates("Product Code")
        df["Product Code"] = df["Product Code"].astype(int)
        df = df.merge(mc[["Product Code","Product Name","2 Classification","Category"]],
                      on="Product Code", how="left")
        df["Full Target Value"] = df["Target (Unit)"] * df["Sales Price"]

        def tv(base_df, factor):
            t = base_df.copy()
            t["Target (Value)"] = (t["Full Target Value"] / 12) * factor
            return t

        def vg(d):
            return d.groupby([id_name], as_index=False)["Target (Value)"].sum()
        def pg(d):
            return d.groupby([id_name,"2 Classification","Category",
                              "Product Code","Product Name",
                              "Target (Unit)","Sales Price"],
                             as_index=False)["Target (Value)"].sum()

        return {
            "full":              df,
            "value_full":        vg(tv(df, 12)),
            "value_month":       vg(tv(df, 1)),
            "value_quarter":     vg(tv(df, 3)),
            "value_uptodate":    vg(tv(df, current_month)),
            "products_full":     pg(tv(df, 12)),
            "products_uptodate": pg(tv(df, current_month)),
            "products_month":    pg(tv(df, 1)),
            "products_quarter":  pg(tv(df, 3)),
        }

    rep        = build_target_pipeline(target_rep_raw,     "Rep Code")
    manager    = build_target_pipeline(target_manager_raw, "Manager Code")
    area       = build_target_pipeline(target_area_raw,    "Area Code")

    # ── SALES ────────────────────────────────────────────────
    sales = sales_raw.copy()
    sales.columns = sales.columns.str.strip()
    expected = ['Date','Warehouse Name','Client Code','Client Name','Notes','MF','Mostanad',
                'Rep Code','Sales Unit Before Edit','Returns Unit Before Edit',
                'Sales Price','Invoice Discounts','Sales Value']
    if len(sales.columns) == len(expected):
        sales.columns = expected
    for col in ['Old Product Code','Old Product Name']:
        if col not in sales.columns: sales[col] = np.nan
        sales[col] = sales[col].astype('object')
    if 'Date' in sales.columns:
        mask = sales['Date'].astype(str).str.strip().eq("كود الصنف")
        sales.loc[mask, 'Old Product Code'] = sales.loc[mask, 'Warehouse Name'].astype('object')
        sales.loc[mask, 'Old Product Name'] = sales.loc[mask, 'Client Code'].astype('object')
        sales[['Old Product Code','Old Product Name']] = sales[['Old Product Code','Old Product Name']].ffill()
        drop_kw = 'المندوب|كود الفرع|تاريخ|كود الصنف'
        sales = sales[sales['Date'].notna()]
        sales = sales[~sales['Date'].astype(str).str.contains(drop_kw, na=False)].copy()
    for col in ['Sales Unit Before Edit','Returns Unit Before Edit','Sales Price','Invoice Discounts','Sales Value']:
        if col in sales.columns:
            sales[col] = pd.to_numeric(sales[col], errors='coerce').fillna(0)
    sales['Old Product Code'] = pd.to_numeric(sales['Old Product Code'], errors='coerce').astype('Int64')
    sales['Rep Code']         = pd.to_numeric(sales['Rep Code'],         errors='coerce').astype('Int64')
    mc = mapping.copy()
    mc_cols = [c for c in ['Old Product Code','4 Classification','Product Name',
                            'Product Code','Category','Next Factor','2 Classification']
               if c in mc.columns]
    sales = sales.merge(mc[mc_cols], on='Old Product Code', how='left')
    if 'Next Factor' not in sales.columns: sales['Next Factor'] = 1
    sales['Next Factor'] = sales['Next Factor'].fillna(1)
    codes['Rep Code'] = pd.to_numeric(codes['Rep Code'], errors='coerce').astype('Int64')
    sales = sales.merge(codes, on='Rep Code', how='left')
    sales['Total Sales Value']         = sales['Sales Unit Before Edit'] * sales['Sales Price']
    sales['Returns Value']             = sales['Returns Unit Before Edit'] * sales['Sales Price']
    sales['Sales After Returns']       = sales['Total Sales Value'] - sales['Returns Value']
    sales['Net Sales Unit Before Edit']= sales['Sales Unit Before Edit'] - sales['Returns Unit Before Edit']
    sales['Net Sales Unit']            = sales['Net Sales Unit Before Edit'] * sales['Next Factor']

    # ── OVERDUE ──────────────────────────────────────────────
    overdue = overdue_raw.iloc[:, :9].copy()
    overdue.columns = ["Client Name","Client Code","15 Days","30 Days","60 Days","90 Days",
                       "120 Days","More Than 120 Days","Balance"]
    overdue['Rep Code']    = pd.Series(dtype='object')
    overdue['Old Rep Name']= pd.Series(dtype='object')
    mask = overdue['Client Name'].astype(str).str.strip().eq("كود المندوب")
    overdue.loc[mask, 'Rep Code']     = overdue.loc[mask, 'Client Code'].astype('object')
    overdue.loc[mask, 'Old Rep Name'] = overdue.loc[mask, '30 Days'].astype('object')
    overdue[['Rep Code','Old Rep Name']] = overdue[['Rep Code','Old Rep Name']].ffill()
    overdue = overdue[
        overdue['Client Name'].notna() &
        (overdue['Client Name'].astype(str).str.strip() != '') &
        (~overdue['Client Name'].astype(str).str.contains(
            'اجمالــــــي التقرير|اجمالى الفرع/المندوب|كود الفرع|كود المندوب|اسم العميل', na=False))
    ].copy()
    for col in ['15 Days','30 Days','60 Days','90 Days','120 Days','More Than 120 Days','Client Code','Rep Code']:
        overdue[col] = pd.to_numeric(overdue[col], errors='coerce').fillna(0)
    overdue['Rep Code']    = overdue['Rep Code'].astype('Int64')
    overdue['Client Code'] = overdue['Client Code'].astype('Int64')
    overdue['Overdue']     = overdue['120 Days'] + overdue['More Than 120 Days']
    overdue = overdue.merge(codes, on='Rep Code', how='left')

    # ── OPENING ──────────────────────────────────────────────
    opening = opening_raw.copy()
    opening.columns = ['Branch','Evak','Opening Balance','Total Sales After Invoice Discounts',
                       'Returns','Sales Value Before Extra Discounts',
                       'Cash Collection','Collection Checks',
                       'Returned Chick','Collection Returned Chick',
                       'Extra Discounts','Daienah','End Balance']
    opening['Rep Code']    = pd.Series(dtype='object')
    opening['Old Rep Name']= pd.Series(dtype='object')
    mask = opening['Branch'].astype(str).str.strip().eq("كود المندوب")
    opening.loc[mask, 'Rep Code']     = opening.loc[mask, 'Opening Balance'].astype('object')
    opening.loc[mask, 'Old Rep Name'] = opening.loc[mask, 'Total Sales After Invoice Discounts'].astype('object')
    opening[['Rep Code','Old Rep Name']] = opening[['Rep Code','Old Rep Name']].ffill()
    opening = opening[
        opening['Branch'].notna() &
        (opening['Branch'].astype(str).str.strip() != '') &
        (~opening['Branch'].astype(str).str.contains('نسبة المندوب|كود المندوب|اجماليات|كود الفرع', na=False))
    ].copy()
    for col in ['Opening Balance','Total Sales After Invoice Discounts','Returns',
                'Sales Value Before Extra Discounts','Cash Collection','Collection Checks',
                'Returned Chick','Collection Returned Chick','Extra Discounts','Daienah','End Balance']:
        opening[col] = pd.to_numeric(opening[col], errors='coerce').fillna(0)
    opening['Total Collection'] = opening['Cash Collection'] + opening['Collection Checks']
    opening['Sales After Returns'] = opening['Total Sales After Invoice Discounts'] - opening['Returns']
    codes['Rep Code'] = pd.to_numeric(codes['Rep Code'], errors='coerce').astype('Int64')
    opening = opening.merge(codes, on='Rep Code', how='left')

    # ── OPENING DETAIL ───────────────────────────────────────
    od = opening_detail_raw.iloc[:, :11].copy()
    od.columns = ['Client Code','Client Name','Opening Balance',
                  'Total Sales After Invoice Discounts','Returns',
                  'Extra Discounts','Total Collection','Madfoaat',
                  'Tasweyat Daiinah','End Balance','Motalbet El Fatrah']
    od['Rep Code']    = pd.Series(dtype='object')
    od['Old Rep Name']= pd.Series(dtype='object')
    mask = od['Client Code'].astype(str).str.strip().eq("كود الفرع")
    od.loc[mask, 'Rep Code']     = od.loc[mask, 'Returns'].astype('object')
    od.loc[mask, 'Old Rep Name'] = od.loc[mask, 'Extra Discounts'].astype('object')
    od[['Rep Code','Old Rep Name']] = od[['Rep Code','Old Rep Name']].ffill()
    od['Rep Code'] = pd.to_numeric(od['Rep Code'], errors='coerce').astype('Int64')
    od = od[
        od['Client Code'].notna() &
        (od['Client Code'].astype(str).str.strip() != '') &
        (~od['Client Code'].astype(str).str.contains("كود الفرع|كود العميل", na=False))
    ].copy()
    od = od.merge(codes, on='Rep Code', how='left')

    return sales, overdue, opening, od, rep, manager, area, codes


# ─────────────────────────────────────────────
#  SIDEBAR FILTERS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:16px 0 8px'>
      <div style='font-size:20px;font-weight:700;color:white'>📊 Sales Dashboard</div>
      <div style='font-size:11px;color:#93B8D8;margin-top:4px'>Sales Performance 2025</div>
    </div>
    <hr style='border-color:rgba(255,255,255,0.1);margin:8px 0 16px'>
    """, unsafe_allow_html=True)

    view_by = st.selectbox("عرض بـ", ["Rep Code","Manager Code","Area Code"], key="view_by")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    try:
        sales, overdue, opening, od, rep, manager, area, codes = process_all()
        data_ok = True

        # Dynamic filter based on view
        all_codes_list = []
        if view_by == "Rep Code" and "Rep Code" in codes.columns:
            all_codes_list = sorted(codes["Rep Code"].dropna().unique().tolist())
        elif view_by == "Manager Code" and "Manager Code" in codes.columns:
            all_codes_list = sorted(codes["Manager Code"].dropna().unique().tolist())
        elif view_by == "Area Code" and "Area Code" in codes.columns:
            all_codes_list = sorted(codes["Area Code"].dropna().unique().tolist())

        selected_code = st.selectbox(
            f"اختر {view_by.replace(' Code','')}",
            ["الكل"] + [str(c) for c in all_codes_list],
            key="selected_code"
        )

        st.markdown("<hr style='border-color:rgba(255,255,255,0.1);margin:12px 0'>", unsafe_allow_html=True)

        # Category filter
        cats = []
        if "Category" in sales.columns:
            cats = sorted(sales["Category"].dropna().unique().tolist())
        selected_cats = st.multiselect("الفئات", cats, default=cats, key="cats")

    except Exception as e:
        data_ok = False
        st.error(f"خطأ في تحميل البيانات:\n{e}")

    st.markdown("""
    <div style='position:fixed;bottom:16px;font-size:10px;color:#556B8A;direction:rtl'>
      © Sales Dashboard 2025
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  MAIN CONTENT
# ─────────────────────────────────────────────
if not data_ok:
    st.error("⚠️ تأكدي من وجود ملفات الإكسيل في نفس مجلد التطبيق")
    st.stop()

# ── FILTER HELPER ────────────────────────────
def filter_df(df, code_col):
    out = df.copy()
    if selected_code != "الكل" and code_col in out.columns:
        try:
            out = out[out[code_col].astype(str) == selected_code]
        except Exception:
            pass
    return out

def filter_sales(df):
    out = df.copy()
    if selected_code != "الكل" and view_by in out.columns:
        try:
            out = out[out[view_by].astype(str) == selected_code]
        except Exception:
            pass
    if selected_cats and "Category" in out.columns:
        out = out[out["Category"].isin(selected_cats)]
    return out

# ── FILTERED DATA ────────────────────────────
sales_f   = filter_sales(sales)
overdue_f = filter_df(overdue,  view_by)
opening_f = filter_df(opening,  view_by)

target_data = {"Rep Code": rep, "Manager Code": manager, "Area Code": area}.get(view_by, rep)
target_id   = view_by

if selected_code != "الكل":
    try:
        sc_num = int(selected_code)
        tv_full  = target_data["value_full"][target_data["value_full"][target_id] == sc_num]["Target (Value)"].sum()
        tv_month = target_data["value_month"][target_data["value_month"][target_id] == sc_num]["Target (Value)"].sum()
        tv_qtr   = target_data["value_quarter"][target_data["value_quarter"][target_id] == sc_num]["Target (Value)"].sum()
        tv_ytd   = target_data["value_uptodate"][target_data["value_uptodate"][target_id] == sc_num]["Target (Value)"].sum()
        prod_tgt = target_data["products_full"][target_data["products_full"][target_id] == sc_num]
    except Exception:
        tv_full = tv_month = tv_qtr = tv_ytd = 0
        prod_tgt = target_data["products_full"].head(0)
else:
    tv_full  = target_data["value_full"]["Target (Value)"].sum()
    tv_month = target_data["value_month"]["Target (Value)"].sum()
    tv_qtr   = target_data["value_quarter"]["Target (Value)"].sum()
    tv_ytd   = target_data["value_uptodate"]["Target (Value)"].sum()
    prod_tgt = target_data["products_full"]

# Sales aggregates
sv_full  = sales_f['Total Sales Value'].sum()
sv_ret   = sales_f['Returns Value'].sum()
sv_sar   = sales_f['Sales After Returns'].sum()
sv_disc  = sales_f['Invoice Discounts'].sum()
sv_month = sales_f[sales_f['Date'].dt.month == current_month]['Total Sales Value'].sum() \
           if 'Date' in sales_f.columns and pd.api.types.is_datetime64_any_dtype(sales_f['Date']) else sv_full

# Collection
ob  = opening_f['Opening Balance'].sum()
cc  = opening_f['Cash Collection'].sum()
ckc = opening_f['Collection Checks'].sum()
exd = opening_f['Extra Discounts'].sum()
eb  = opening_f['End Balance'].sum()
tot_col = cc + ckc
od_total = overdue_f['Overdue'].sum()

# ─────────────────────────────────────────────
#  TOP BANNER
# ─────────────────────────────────────────────
who = selected_code if selected_code != "الكل" else "الكل"
st.markdown(f"""
<div class="top-banner">
  <div>
    <h1>📊 Sales Performance Dashboard</h1>
    <p>عرض بـ: {view_by} &nbsp;|&nbsp; {who} &nbsp;|&nbsp; FY 2025 — شهر {current_month}</p>
  </div>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
#  TABS
# ════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 Target & Achievement",
    "💰 Sales Analysis",
    "🏦 Collection & Overdue",
    "📦 Product Analysis",
    "👥 Customer Analysis",
])


# ══════════════════════════════════════════════
#  TAB 1: TARGET & ACHIEVEMENT
# ══════════════════════════════════════════════
with tab1:
    st.markdown("""
    <div class="sec-header">
      <div class="sec-icon" style="background:#E6F1FB">🎯</div>
      <div class="sec-title">Target & Achievement</div>
      <div class="sec-subtitle">نسب التحقيق — سنوي · شهري · ربعي · Up to Date</div>
    </div>""", unsafe_allow_html=True)

    pct_full  = (sv_full  / tv_full  * 100) if tv_full  else 0
    pct_month = (sv_month / tv_month * 100) if tv_month else 0
    pct_qtr   = (sv_sar   / tv_qtr   * 100) if tv_qtr   else 0
    pct_ytd   = (sv_sar   / tv_ytd   * 100) if tv_ytd   else 0

    # KPI row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Target Full Year", fmt_k(tv_full), f"Achieved: {fmt_k(sv_full)}")
    with c2:
        st.metric("Target Up to Date", fmt_k(tv_ytd), f"Achieved: {fmt_k(sv_sar)}")
    with c3:
        st.metric("Target Quarter", fmt_k(tv_qtr), f"Achieved: {fmt_k(sv_sar)}")
    with c4:
        st.metric("Target Month", fmt_k(tv_month), f"Achieved: {fmt_k(sv_month)}")

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # Gauge row
    g1, g2, g3, g4 = st.columns(4)
    for col, pct, title, color in [
        (g1, pct_full,  "Full Year %",    pct_color(pct_full)),
        (g2, pct_ytd,   "Up to Date %",   pct_color(pct_ytd)),
        (g3, pct_qtr,   "Quarter %",      pct_color(pct_qtr)),
        (g4, pct_month, "Month %",        pct_color(pct_month)),
    ]:
        with col:
            st.plotly_chart(make_gauge(pct, 120, color, title),
                            use_container_width=True, config={"displayModeBar": False})

    # Achievement trend (if enough data)
    if 'Date' in sales_f.columns and pd.api.types.is_datetime64_any_dtype(sales_f['Date']):
        st.markdown("""
        <div class="sec-header" style="margin-top:1rem">
          <div class="sec-icon" style="background:#E1F5EE">📈</div>
          <div class="sec-title">Monthly Sales vs Target Trend</div>
        </div>""", unsafe_allow_html=True)

        monthly = (sales_f.groupby(sales_f['Date'].dt.month)['Total Sales Value']
                   .sum().reset_index())
        monthly.columns = ['Month', 'Sales']

        month_tgt = tv_full / 12
        monthly['Target'] = month_tgt
        monthly['Achievement %'] = (monthly['Sales'] / monthly['Target'] * 100).round(1)

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(
            x=monthly['Month'], y=monthly['Sales'],
            name='Sales', marker_color=C_BLUE, opacity=0.85
        ), secondary_y=False)
        fig.add_trace(go.Scatter(
            x=monthly['Month'], y=monthly['Target'],
            name='Target', line=dict(color=C_RED, width=2, dash='dot'),
            mode='lines+markers', marker=dict(size=5)
        ), secondary_y=False)
        fig.add_trace(go.Scatter(
            x=monthly['Month'], y=monthly['Achievement %'],
            name='Achievement %', line=dict(color=C_GREEN, width=2),
            mode='lines+markers', marker=dict(size=6),
            yaxis="y2"
        ), secondary_y=True)
        fig.update_layout(
            height=300, margin=dict(t=10, b=30, l=40, r=40),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor=C_LGRAY,
            legend=dict(orientation='h', y=1.05),
            xaxis=dict(title="Month", dtick=1, gridcolor='white'),
            yaxis=dict(title="Value (EGP)", gridcolor='white'),
        )
        fig.update_yaxes(title_text="Achievement %", secondary_y=True)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ══════════════════════════════════════════════
#  TAB 2: SALES ANALYSIS
# ══════════════════════════════════════════════
with tab2:
    st.markdown("""
    <div class="sec-header">
      <div class="sec-icon" style="background:#E1F5EE">💰</div>
      <div class="sec-title">Sales Analysis</div>
      <div class="sec-subtitle">إجمالي · بعد المرتجع · بعد الخصم · صافي</div>
    </div>""", unsafe_allow_html=True)

    net_sales = sv_sar - sv_disc

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Total Sales (Gross)",   fmt_k(sv_full))
    with c2: st.metric("Returns Value",          fmt_k(sv_ret),  f"-{sv_ret/sv_full*100:.1f}%" if sv_full else "0%")
    with c3: st.metric("Sales After Returns",    fmt_k(sv_sar))
    with c4: st.metric("Net Sales (after disc)", fmt_k(net_sales))

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    col_a, col_b = st.columns([1.5, 1])

    with col_a:
        st.markdown("**Waterfall — من الإجمالي للصافي**")
        wf_labels = ["Total Sales","— Returns","After Returns","— Inv. Discounts","Net Sales"]
        wf_values = [sv_full, -sv_ret, sv_sar, -sv_disc, net_sales]
        wf_colors = [C_BLUE, C_RED, C_TEAL, C_ORANGE, C_GREEN]

        fig_wf = go.Figure(go.Waterfall(
            orientation="v", measure=["absolute","relative","absolute","relative","absolute"],
            x=wf_labels, y=[sv_full, -sv_ret, sv_sar, -sv_disc, net_sales],
            text=[fmt_k(abs(v)) for v in wf_values],
            textposition="outside",
            connector={"line": {"color": "#ccc", "width": 1}},
            increasing={"marker": {"color": C_GREEN}},
            decreasing={"marker": {"color": C_RED}},
            totals={"marker": {"color": C_BLUE}},
        ))
        fig_wf.update_layout(
            height=320, margin=dict(t=20, b=20, l=20, r=20),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor=C_LGRAY,
            showlegend=False, yaxis=dict(gridcolor='white')
        )
        st.plotly_chart(fig_wf, use_container_width=True, config={"displayModeBar": False})

    with col_b:
        st.markdown("**Discount Breakdown**")
        disc_data = {
            "Invoice Discounts": sv_disc,
            "Extra Discounts":   exd,
            "Returns":           sv_ret,
        }
        disc_df = pd.DataFrame(disc_data.items(), columns=['Type', 'Value'])
        fig_pie = px.pie(disc_df, names='Type', values='Value',
                         color_discrete_sequence=[C_ORANGE, C_RED, C_TEAL],
                         hole=0.55)
        fig_pie.update_traces(textinfo='percent+label', textfont_size=11)
        fig_pie.update_layout(
            height=320, margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor='rgba(0,0,0,0)', showlegend=False
        )
        st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

    # Sales by category
    if "Category" in sales_f.columns:
        st.markdown("""
        <div class="sec-header" style="margin-top:1rem">
          <div class="sec-icon" style="background:#EEEDFE">📊</div>
          <div class="sec-title">Sales by Category</div>
        </div>""", unsafe_allow_html=True)

        cat_sales = (sales_f.groupby('Category')[['Total Sales Value','Returns Value','Sales After Returns']]
                     .sum().reset_index().sort_values('Sales After Returns', ascending=False))
        fig_cat = px.bar(cat_sales, x='Category',
                         y=['Total Sales Value','Returns Value','Sales After Returns'],
                         barmode='group',
                         color_discrete_map={
                             'Total Sales Value':   C_BLUE,
                             'Returns Value':       C_RED,
                             'Sales After Returns': C_GREEN
                         })
        fig_cat.update_layout(
            height=300, margin=dict(t=10, b=30, l=40, r=20),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor=C_LGRAY,
            legend=dict(orientation='h', y=1.05),
            yaxis=dict(gridcolor='white')
        )
        st.plotly_chart(fig_cat, use_container_width=True, config={"displayModeBar": False})


# ══════════════════════════════════════════════
#  TAB 3: COLLECTION & OVERDUE
# ══════════════════════════════════════════════
with tab3:
    st.markdown("""
    <div class="sec-header">
      <div class="sec-icon" style="background:#FAEEDA">🏦</div>
      <div class="sec-title">Collection & Overdue</div>
      <div class="sec-subtitle">تحصيل · مديونية · رصيد</div>
    </div>""", unsafe_allow_html=True)

    pct_col  = (tot_col / ob * 100)   if ob      else 0
    pct_od   = (tot_col / od_total * 100) if od_total else 0
    rem_2025_pct = (eb / ob * 100)    if ob      else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.metric("Opening Balance",   fmt_k(ob))
    with c2: st.metric("Cash Collection",   fmt_k(cc))
    with c3: st.metric("Collection Checks", fmt_k(ckc))
    with c4: st.metric("Extra Discounts",   fmt_k(exd))
    with c5: st.metric("End Balance",       fmt_k(eb))

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    c_left, c_right = st.columns(2)

    with c_left:
        st.markdown("**Collection Flow**")
        flow_fig = go.Figure()
        flow_fig.add_trace(go.Bar(
            x=["Opening\nBalance", "Cash\nCollection", "Collection\nChecks",
               "— Extra\nDiscounts", "End\nBalance"],
            y=[ob, cc, ckc, -exd, eb],
            marker_color=[C_NAVY, C_GREEN, C_TEAL, C_RED, C_BLUE],
            text=[fmt_k(abs(v)) for v in [ob, cc, ckc, exd, eb]],
            textposition='outside'
        ))
        flow_fig.update_layout(
            height=300, margin=dict(t=20, b=20, l=20, r=20),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor=C_LGRAY,
            showlegend=False, yaxis=dict(gridcolor='white')
        )
        st.plotly_chart(flow_fig, use_container_width=True, config={"displayModeBar": False})

    with c_right:
        st.markdown("**Collection KPIs**")
        kpi_col1, kpi_col2 = st.columns(2)
        with kpi_col1:
            st.metric("Total Collection", fmt_k(tot_col))
            st.metric("Overdue Total",    fmt_k(od_total))
        with kpi_col2:
            st.metric("Collected %",         f"{pct_col:.1f}%")
            st.metric("Collection/Overdue %", f"{pct_od:.1f}%")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # Remaining from 2025
        rem = ob - tot_col + exd
        st.metric("Remaining from 2025", fmt_k(rem),
                  f"{rem/ob*100:.1f}% of opening" if ob else "—")

    # Overdue aging
    st.markdown("""
    <div class="sec-header" style="margin-top:1rem">
      <div class="sec-icon" style="background:#FCEBEB">⚠️</div>
      <div class="sec-title">Overdue Aging Buckets</div>
    </div>""", unsafe_allow_html=True)

    aging_cols = ["15 Days","30 Days","60 Days","90 Days","120 Days","More Than 120 Days"]
    existing_aging = [c for c in aging_cols if c in overdue_f.columns]
    if existing_aging:
        aging_vals = overdue_f[existing_aging].sum()
        fig_aging = px.bar(
            x=aging_vals.index, y=aging_vals.values,
            color=aging_vals.values,
            color_continuous_scale=["#EAF3DE","#FAEEDA","#FCEBEB","#F7C1C1","#E24B4A","#A32D2D"],
            text=[fmt_k(v) for v in aging_vals.values]
        )
        fig_aging.update_traces(textposition='outside')
        fig_aging.update_layout(
            height=280, margin=dict(t=10, b=20, l=40, r=20),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor=C_LGRAY,
            showlegend=False, coloraxis_showscale=False,
            yaxis=dict(gridcolor='white')
        )
        st.plotly_chart(fig_aging, use_container_width=True, config={"displayModeBar": False})


# ══════════════════════════════════════════════
#  TAB 4: PRODUCT ANALYSIS
# ══════════════════════════════════════════════
with tab4:
    st.markdown("""
    <div class="sec-header">
      <div class="sec-icon" style="background:#EEEDFE">📦</div>
      <div class="sec-title">Product Analysis</div>
      <div class="sec-subtitle">كاتيجوري · عدد المنتجات المحققة · نسبة تحقيق</div>
    </div>""", unsafe_allow_html=True)

    # Join target products with actual sales products
    if "Product Code" in sales_f.columns and "Product Code" in prod_tgt.columns:
        prod_sales = (sales_f.groupby(["Product Code","Category"])
                      ['Net Sales Unit'].sum().reset_index())
        prod_merge = prod_tgt.merge(prod_sales, on="Product Code", how="left")
        prod_merge['Net Sales Unit'] = prod_merge['Net Sales Unit'].fillna(0)
        prod_merge['Achieved'] = prod_merge['Net Sales Unit'] >= prod_merge['Target (Unit)']

        # Category summary
        cat_summary = prod_merge.groupby("Category").agg(
            Total_Products    = ('Product Code', 'count'),
            Achieved_Products = ('Achieved',      'sum'),
            Total_Target_Val  = ('Target (Value)', 'sum'),
        ).reset_index()
        cat_summary['Not_Achieved']   = cat_summary['Total_Products'] - cat_summary['Achieved_Products']
        cat_summary['Achievement_%']  = (cat_summary['Achieved_Products'] / cat_summary['Total_Products'] * 100).round(1)

        # Summary KPIs
        total_prods = int(cat_summary['Total_Products'].sum())
        total_ach   = int(cat_summary['Achieved_Products'].sum())
        total_not   = total_prods - total_ach

        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Total Products",       total_prods)
        with c2: st.metric("Achieved Target ✅",   total_ach, f"{total_ach/total_prods*100:.1f}%" if total_prods else "0%")
        with c3: st.metric("Not Achieved ❌",       total_not, f"-{total_not/total_prods*100:.1f}%" if total_prods else "0%")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        c_left, c_right = st.columns([1.4, 1])

        with c_left:
            st.markdown("**Achievement by Category**")
            fig_cat_ach = go.Figure()
            fig_cat_ach.add_trace(go.Bar(
                name='Achieved', x=cat_summary['Category'],
                y=cat_summary['Achieved_Products'],
                marker_color=C_GREEN, text=cat_summary['Achieved_Products'], textposition='inside'
            ))
            fig_cat_ach.add_trace(go.Bar(
                name='Not Achieved', x=cat_summary['Category'],
                y=cat_summary['Not_Achieved'],
                marker_color=C_RED, text=cat_summary['Not_Achieved'], textposition='inside'
            ))
            fig_cat_ach.update_layout(
                barmode='stack', height=300,
                margin=dict(t=10, b=20, l=20, r=20),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor=C_LGRAY,
                legend=dict(orientation='h', y=1.05),
                yaxis=dict(title="# Products", gridcolor='white')
            )
            st.plotly_chart(fig_cat_ach, use_container_width=True, config={"displayModeBar": False})

        with c_right:
            st.markdown("**Achievement % per Category**")
            fig_pct = px.bar(
                cat_summary.sort_values('Achievement_%', ascending=True),
                x='Achievement_%', y='Category',
                orientation='h', text='Achievement_%',
                color='Achievement_%',
                color_continuous_scale=["#E24B4A","#ED7D31","#70AD47"],
                range_color=[0,100]
            )
            fig_pct.update_traces(texttemplate='%{text:.0f}%', textposition='outside')
            fig_pct.update_layout(
                height=300, margin=dict(t=10, b=20, l=20, r=40),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor=C_LGRAY,
                showlegend=False, coloraxis_showscale=False,
                xaxis=dict(range=[0,120], gridcolor='white')
            )
            st.plotly_chart(fig_pct, use_container_width=True, config={"displayModeBar": False})

        # Detailed table
        st.markdown("**Category Detail Table**")
        display_cat = cat_summary.copy()
        display_cat['Total Target Value'] = display_cat['Total_Target_Val'].apply(fmt_k)
        display_cat['Achievement %'] = display_cat['Achievement_%'].apply(lambda x: f"{x:.1f}%")
        st.dataframe(
            display_cat[['Category','Total_Products','Achieved_Products','Not_Achieved','Achievement %','Total Target Value']]
            .rename(columns={'Total_Products':'Total','Achieved_Products':'Achieved','Not_Achieved':'Not Achieved'}),
            use_container_width=True, hide_index=True
        )
    else:
        st.info("لا توجد بيانات كافية لتحليل المنتجات مع الفلتر الحالي.")


# ══════════════════════════════════════════════
#  TAB 5: CUSTOMER ANALYSIS
# ══════════════════════════════════════════════
with tab5:
    st.markdown("""
    <div class="sec-header">
      <div class="sec-icon" style="background:#FBEAF0">👥</div>
      <div class="sec-title">Customer Analysis</div>
      <div class="sec-subtitle">إجمالي · نشط · غير نشط</div>
    </div>""", unsafe_allow_html=True)

    if 'Client Code' in sales_f.columns:
        all_clients    = sales_f['Client Code'].nunique()
        active_clients = sales_f.groupby('Client Code')['Total Sales Value'].sum()
        active         = int((active_clients > 0).sum())
        inactive       = all_clients - active

        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Total Customers",   all_clients)
        with c2: st.metric("Active Customers ✅", active,   f"{active/all_clients*100:.1f}%" if all_clients else "0%")
        with c3: st.metric("Inactive Customers", inactive,  f"{inactive/all_clients*100:.1f}%" if all_clients else "0%")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        c_left, c_right = st.columns(2)

        with c_left:
            # Active vs Inactive donut
            fig_cu = go.Figure(go.Pie(
                labels=["Active","Inactive"],
                values=[active, inactive],
                hole=0.6,
                marker_colors=[C_GREEN, C_RED],
                textinfo='percent+label', textfont_size=12
            ))
            fig_cu.update_layout(
                height=280, margin=dict(t=20, b=10, l=10, r=10),
                paper_bgcolor='rgba(0,0,0,0)', showlegend=False,
                annotations=[dict(text=f"{active}<br><span style='font-size:10'>Active</span>",
                                  x=0.5, y=0.5, font_size=18, showarrow=False)]
            )
            st.plotly_chart(fig_cu, use_container_width=True, config={"displayModeBar": False})

        with c_right:
            # Top 10 customers
            top_cu = (sales_f.groupby(['Client Code','Client Name'])['Total Sales Value']
                      .sum().reset_index()
                      .sort_values('Total Sales Value', ascending=False).head(10))
            fig_top = px.bar(
                top_cu, x='Total Sales Value', y='Client Name',
                orientation='h', text='Total Sales Value',
                color_discrete_sequence=[C_BLUE]
            )
            fig_top.update_traces(
                texttemplate=[fmt_k(v) for v in top_cu['Total Sales Value']],
                textposition='outside'
            )
            fig_top.update_layout(
                height=320, margin=dict(t=10, b=10, l=10, r=40),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor=C_LGRAY,
                showlegend=False, yaxis=dict(autorange='reversed'),
                xaxis=dict(gridcolor='white')
            )
            st.plotly_chart(fig_top, use_container_width=True, config={"displayModeBar": False})

        # Customers with overdue
        if 'Client Code' in overdue_f.columns:
            cu_od = overdue_f[overdue_f['Overdue'] > 0][['Client Code','Client Name','Overdue']] \
                    .sort_values('Overdue', ascending=False).head(15)
            if not cu_od.empty:
                st.markdown("""
                <div class="sec-header" style="margin-top:1rem">
                  <div class="sec-icon" style="background:#FCEBEB">⚠️</div>
                  <div class="sec-title">Top Customers with Overdue</div>
                </div>""", unsafe_allow_html=True)
                cu_od['Overdue (fmt)'] = cu_od['Overdue'].apply(fmt_k)
                st.dataframe(cu_od[['Client Code','Client Name','Overdue (fmt)']],
                             use_container_width=True, hide_index=True)
    else:
        st.info("لا توجد بيانات عملاء مع الفلتر الحالي.")
