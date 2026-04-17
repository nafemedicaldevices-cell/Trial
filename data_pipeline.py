import pandas as pd
import numpy as np
import streamlit as st

# =========================
# TIME SETTINGS
# =========================
current_month = pd.Timestamp.today().month
current_quarter = (current_month - 1) // 3 + 1

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    return {
        "target_rep":        pd.read_excel("Target Rep.xlsx"),
        "target_manager":    pd.read_excel("Target Manager.xlsx"),
        "target_area":       pd.read_excel("Target Area.xlsx"),
        "target_supervisor": pd.read_excel("Target Supervisor.xlsx"),
        "target_evak":       pd.read_excel("Target Evak.xlsx"),
        "sales":             pd.read_excel("Sales.xlsx", header=None),
        "mapping":           pd.read_excel("Mapping.xlsx"),
        "codes":             pd.read_excel("Code.xlsx"),
        "opening":           pd.read_excel("Opening.xlsx", header=None),
        "overdue":           pd.read_excel("Overdue.xlsx", header=None),
    }

# =========================
# FIX SALES COLUMNS
# =========================
def fix_sales_columns(sales):
    expected_cols = [
        'Date','Warehouse Name','Client Code','Client Name','Notes','MF','Mostanad',
        'Rep Code','Sales Unit Before Edit','Returns Unit Before Edit',
        'Sales Price','Invoice Discounts','Sales Value'
    ]
    sales = sales.iloc[:, :len(expected_cols)].copy()
    sales.columns = expected_cols
    return sales

# =========================
# TARGET PIPELINE
# =========================
def build_target_pipeline(df, id_name, mapping):
    df = df.copy()
    mapping = mapping.copy()
    df.columns = df.columns.str.strip()
    mapping.columns = mapping.columns.str.strip()

    if "Product Code" not in df.columns:
        df["Product Code"] = np.nan
    if "Product Name" not in df.columns:
        df["Product Name"] = np.nan
    if "Sales Price" not in df.columns:
        df["Sales Price"] = 0

    df["Product Code"] = pd.to_numeric(df["Product Code"], errors="coerce")
    mapping["Product Code"] = pd.to_numeric(mapping["Product Code"], errors="coerce")
    mapping = mapping.drop_duplicates("Product Code")

    fixed_cols = [c for c in ["Year", "Product Code", "Old Product Name", "Sales Price"] if c in df.columns]
    dynamic_cols = [c for c in df.columns if c not in fixed_cols]

    df = df.melt(id_vars=fixed_cols, value_vars=dynamic_cols,
                 var_name=id_name, value_name="Target (Unit)")

    df[id_name] = pd.to_numeric(
        df[id_name].astype(str).str.replace(r"[^0-9]", "", regex=True),
        errors="coerce"
    )

    if "Product Name" in mapping.columns:
        df = df.merge(mapping[["Product Code", "Product Name"]], on="Product Code", how="left")

    df["Target (Unit)"] = pd.to_numeric(df["Target (Unit)"], errors="coerce").fillna(0)
    df["Sales Price"]   = pd.to_numeric(df["Sales Price"],   errors="coerce").fillna(0)
    df["Value"] = df["Target (Unit)"] * df["Sales Price"]

    full    = df.copy()
    month   = df.copy(); month["Value"]   = month["Value"]   * (current_month   / 12)
    quarter = df.copy(); quarter["Value"] = quarter["Value"] * (current_quarter / 4)
    ytd     = df.copy(); ytd["Value"]     = ytd["Value"]     * (current_month   / 12)

    def grp(d):
        return d.groupby([id_name], as_index=False)["Value"].sum()

    value_table = grp(full).rename(columns={"Value": "Full Year"})
    value_table = value_table.merge(grp(month).rename(columns={"Value": "Month"}),     on=id_name, how="left")
    value_table = value_table.merge(grp(quarter).rename(columns={"Value": "Quarter"}), on=id_name, how="left")
    value_table = value_table.merge(grp(ytd).rename(columns={"Value": "YTD"}),         on=id_name, how="left")

    def product_group(d):
        if "Product Code" not in d.columns:
            d["Product Code"] = np.nan
        if "Product Name" not in d.columns:
            d["Product Name"] = "Unknown"
        return d.groupby([id_name, "Product Code", "Product Name"], as_index=False).agg(
            Units=("Target (Unit)", "sum"),
            Value=("Value", "sum")
        )

    return {
        "value_table":     value_table,
        "products_full":   product_group(full),
        "products_month":  product_group(month),
        "products_quarter":product_group(quarter),
        "products_ytd":    product_group(ytd),
    }

# =========================
# SALES PIPELINE
# =========================
def build_sales_pipeline(sales, codes):
    sales = fix_sales_columns(sales)
    sales.columns = sales.columns.str.strip()
    codes.columns = codes.columns.str.strip()

    for col in ["Sales Unit Before Edit","Returns Unit Before Edit","Sales Price","Invoice Discounts"]:
        sales[col] = pd.to_numeric(sales[col], errors="coerce").fillna(0)

    sales["Rep Code"] = pd.to_numeric(sales["Rep Code"], errors="coerce")
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")
    sales = sales.merge(codes, on="Rep Code", how="inner")

    if sales.empty:
        return {k: pd.DataFrame() for k in ["rep","manager","area","supervisor","_raw"]}

    sales["Total Sales Value"]   = sales["Sales Unit Before Edit"]   * sales["Sales Price"]
    sales["Returns Value"]       = sales["Returns Unit Before Edit"] * sales["Sales Price"]
    sales["Sales After Returns"] = sales["Total Sales Value"] - sales["Returns Value"]

    def grp(df, col):
        if col not in df.columns:
            return pd.DataFrame()
        return df.groupby(col, as_index=False)[
            ["Total Sales Value","Returns Value","Sales After Returns","Invoice Discounts"]
        ].sum()

    return {
        "rep":        grp(sales, "Rep Code"),
        "manager":    grp(sales, "Manager Code"),
        "area":       grp(sales, "Area Code"),
        "supervisor": grp(sales, "Supervisor Code"),
        "_raw":       sales,
    }

# =========================
# OPENING PIPELINE
# =========================
def build_opening_pipeline(opening, codes):
    opening.columns = [
        'Branch',"Evak",'Opening Balance','Total Sales','Returns',
        'Sales Value Before Extra Discounts','Cash Collection','Collection Checks',
        'Returned Chick','Collection Returned Chick',"Madinah",'Daienah','End Balance'
    ]
    opening['Rep Code'] = None
    mask = opening['Branch'].astype(str).str.strip() == "كود المندوب"
    opening.loc[mask, 'Rep Code'] = opening.loc[mask, 'Opening Balance']
    opening['Rep Code'] = opening['Rep Code'].ffill()
    opening = opening[
        opening['Branch'].notna() &
        (~opening['Branch'].astype(str).str.contains('كود|اجماليات', na=False))
    ]
    for col in ['Opening Balance','Total Sales','Returns','Cash Collection','Collection Checks','End Balance']:
        opening[col] = pd.to_numeric(opening[col], errors='coerce').fillna(0)

    opening['Total Collection']    = opening['Cash Collection'] + opening['Collection Checks']
    opening["Sales After Returns"] = opening["Total Sales"] - opening['Returns']
    opening["Rep Code"] = pd.to_numeric(opening["Rep Code"], errors="coerce")
    codes["Rep Code"]   = pd.to_numeric(codes["Rep Code"],   errors="coerce")
    opening = opening.merge(codes, on='Rep Code', how='left')
    opening.rename(columns={"Total Sales": "Total Sales Value", "Returns": "Returns Value"}, inplace=True)

    def grp(df, col):
        return df.groupby(col, as_index=False)[
            ["Total Sales Value","Returns Value","Sales After Returns","Total Collection"]
        ].sum()

    return {
        "rep":        grp(opening, "Rep Code"),
        "manager":    grp(opening, "Manager Code"),
        "area":       grp(opening, "Area Code"),
        "supervisor": grp(opening, "Supervisor Code"),
    }

# =========================
# OVERDUE PIPELINE
# =========================
def build_overdue_pipeline(overdue, codes):
    overdue = overdue.copy()
    codes   = codes.copy()
    overdue.columns = [
        "Client Name","Client Code","30 Days","60 Days","90 Days",
        "120 Days","150 Days","More Than 150 Days","Balance"
    ]
    overdue['Rep Code'] = None
    overdue['Old Rep Name'] = None
    mask = overdue['Client Name'].astype(str).str.strip() == "كود المندوب"
    overdue.loc[mask, 'Rep Code']     = overdue.loc[mask, 'Client Code']
    overdue.loc[mask, 'Old Rep Name'] = overdue.loc[mask, '30 Days']
    overdue[['Rep Code','Old Rep Name']] = overdue[['Rep Code','Old Rep Name']].ffill()
    overdue = overdue[
        overdue['Client Name'].notna() &
        (overdue['Client Name'].astype(str).str.strip() != '') &
        (~overdue['Client Name'].astype(str).str.contains(
            'اجمالــــــي التقرير|اجمالى الفرع/المندوب|كود الفرع|كود المندوب|اسم العميل', na=False))
    ].copy()

    for col in ['30 Days','60 Days','90 Days','120 Days','150 Days','More Than 150 Days','Client Code','Rep Code']:
        overdue[col] = pd.to_numeric(overdue[col], errors='coerce').fillna(0)

    overdue['Rep Code'] = overdue['Rep Code'].astype(int)
    overdue['Overdue Value'] = overdue['120 Days'] + overdue['150 Days'] + overdue['More Than 150 Days']
    overdue['Total Balance']  = overdue[['30 Days','60 Days','90 Days','120 Days','150 Days','More Than 150 Days']].sum(axis=1)
    overdue = overdue.merge(
        codes[['Rep Code','Rep Name','Area Name','Area Code','Manager Name','Manager Code','Supervisor Code']],
        on='Rep Code', how='left'
    )

    def grp(df, col):
        if col not in df.columns:
            return pd.DataFrame()
        return df.groupby(col, as_index=False)[["Overdue Value","Total Balance"]].sum()

    return {
        "rep":        grp(overdue, "Rep Code"),
        "manager":    grp(overdue, "Manager Code"),
        "area":       grp(overdue, "Area Code"),
        "supervisor": grp(overdue, "Supervisor Code"),
    }

# =========================
# HELPERS
# =========================
def fmt(v):
    if pd.isna(v):
        return "0"
    v = float(v)
    if abs(v) >= 1_000_000:
        return f"{v/1_000_000:.2f}M"
    elif abs(v) >= 1_000:
        return f"{v/1_000:.1f}K"
    return f"{v:,.0f}"

def pct_color(p):
    if p >= 100: return "#3B6D11", "#EAF3DE"
    if p >= 70:  return "#854F0B", "#FAEEDA"
    return "#A32D2D", "#FCEBEB"

def kpi_card(title, actual, target):
    p = (actual / target * 100) if target else 0
    tc, bg = pct_color(p)
    bar = min(p, 100)
    return f"""
    <div style="background:white;padding:14px;border-radius:12px;
                border:0.5px solid #e0e0e0;border-top:4px solid {tc};">
      <div style="font-size:12px;color:#666;margin-bottom:6px;">{title}</div>
      <div style="font-size:22px;font-weight:600;color:#1a1a1a;">{fmt(actual)}</div>
      <div style="font-size:11px;color:#999;margin:2px 0 6px;">تارجت: {fmt(target)}</div>
      <div style="background:#eee;border-radius:99px;height:5px;">
        <div style="background:{tc};width:{bar:.1f}%;height:5px;border-radius:99px;"></div>
      </div>
      <div style="font-size:13px;font-weight:600;color:{tc};margin-top:5px;">{p:.1f}%</div>
    </div>"""

def sales_flow_html(total, returns, inv_disc, extra_disc):
    after_ret = total - returns
    net = after_ret - inv_disc - extra_disc

    def row(label, val, color, bg):
        return f"""
        <div style="background:{bg};border:0.5px solid {color};border-radius:8px;
                    padding:10px 14px;display:flex;justify-content:space-between;align-items:center;">
          <span style="font-size:13px;font-weight:600;color:{color};">{label}</span>
          <span style="font-size:13px;font-weight:600;color:{color};">{fmt(val)}</span>
        </div>"""

    def branch(label, val):
        return f"""
        <div style="display:flex;align-items:center;margin:2px 0;">
          <div style="width:24px;border-bottom:1.5px dashed #A32D2D;margin-left:8px;"></div>
          <div style="background:#FCEBEB;border:0.5px solid #A32D2D;border-radius:6px;
                      padding:5px 10px;display:flex;justify-content:space-between;
                      gap:16px;flex:1;">
            <span style="font-size:12px;color:#791F1F;font-weight:500;">{label}</span>
            <span style="font-size:12px;color:#A32D2D;font-weight:600;">- {fmt(val)}</span>
          </div>
        </div>"""

    def arrow(color="#185FA5"):
        return f"""<div style="text-align:center;color:{color};font-size:18px;
                               line-height:1;margin:2px 0;">↓</div>"""

    def dot():
        return """<div style="display:flex;align-items:center;margin:0;">
          <div style="width:8px;height:8px;border-radius:50%;background:#185FA5;margin:2px auto;"></div>
        </div>"""

    return f"""
    <div style="display:flex;flex-direction:column;gap:0;padding:4px 0;">
      {row("إجمالي المبيعات", total, "#0C447C", "#E6F1FB")}
      {dot()}
      {branch("مرتجعات البيع", returns)}
      {arrow()}
      {row("بعد المرتجعات", after_ret, "#0C447C", "#E6F1FB")}
      {dot()}
      {branch("خصومات عادية", inv_disc)}
      {dot()}
      {branch("خصومات إضافية", extra_disc)}
      {arrow("#3B6D11")}
      {row("صافي المبيعات النهائي", net, "#27500A", "#EAF3DE")}
    </div>"""

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(layout="wide", page_title="KPI Dashboard")

st.markdown("""
<style>
[data-testid="stSidebar"] { background: #f8f9fa; }
.block-container { padding-top: 1.5rem; }
h1 { font-size: 22px !important; }
h2 { font-size: 17px !important; border-bottom: 0.5px solid #e0e0e0; padding-bottom: 6px; margin-bottom: 12px; }
h3 { font-size: 14px !important; color: #555; }
</style>
""", unsafe_allow_html=True)

# =========================
# LOAD
# =========================
data = load_data()
codes = data["codes"].copy()
codes.columns = codes.columns.str.strip()

sales_data   = build_sales_pipeline(data["sales"],   data["codes"])
opening_data = build_opening_pipeline(data["opening"], data["codes"])
overdue_data = build_overdue_pipeline(data["overdue"], data["codes"])

target_rep        = build_target_pipeline(data["target_rep"],        "Rep Code",        data["mapping"])
target_manager    = build_target_pipeline(data["target_manager"],    "Manager Code",    data["mapping"])
target_area       = build_target_pipeline(data["target_area"],       "Area Code",       data["mapping"])
target_supervisor = build_target_pipeline(data["target_supervisor"], "Supervisor Code", data["mapping"])

# =========================
# SIDEBAR FILTER
# =========================
st.sidebar.title("الفلاتر")

filter_type = st.sidebar.radio("عرض حسب", ["مندوب", "مشرف", "منطقة", "مدير"])

level_map = {
    "مندوب":  ("Rep Code",        "rep",        target_rep),
    "مشرف":   ("Supervisor Code", "supervisor", target_supervisor),
    "منطقة":  ("Area Code",       "area",       target_area),
    "مدير":   ("Manager Code",    "manager",    target_manager),
}
id_col, dict_key, tgt_pipeline = level_map[filter_type]

# Build label map from codes
label_cols = {
    "Rep Code":        "Rep Name",
    "Supervisor Code": "Supervisor Name",
    "Area Code":       "Area Name",
    "Manager Code":    "Manager Name",
}
name_col = label_cols[id_col]

if id_col in codes.columns and name_col in codes.columns:
    id_label = (
        codes[[id_col, name_col]]
        .dropna(subset=[id_col, name_col])
        .drop_duplicates(id_col)
        .set_index(id_col)[name_col]
        .to_dict()
    )
else:
    id_label = {}

# Get available IDs from sales
sales_df = sales_data.get(dict_key, pd.DataFrame())
if not sales_df.empty and id_col in sales_df.columns:
    available_ids = sales_df[id_col].dropna().unique().tolist()
else:
    available_ids = list(id_label.keys())

options = {str(i): id_label.get(i, f"#{i}") for i in available_ids}
selected_label = st.sidebar.selectbox(
    "اختر",
    options=list(options.values()),
    format_func=lambda x: x
)
selected_id = next((k for k, v in options.items() if v == selected_label), None)
selected_id_num = pd.to_numeric(selected_id, errors="coerce")

def get_row(df, col, val):
    if df.empty or col not in df.columns:
        return pd.Series(dtype=float)
    row = df[df[col] == val]
    return row.iloc[0] if not row.empty else pd.Series(dtype=float)

s_row  = get_row(sales_data.get(dict_key,   pd.DataFrame()), id_col, selected_id_num)
op_row = get_row(opening_data.get(dict_key, pd.DataFrame()), id_col, selected_id_num)
ov_row = get_row(overdue_data.get(dict_key, pd.DataFrame()), id_col, selected_id_num)
tgt_row = get_row(tgt_pipeline["value_table"], id_col, selected_id_num)

def safe(row, col, default=0):
    try:
        v = row.get(col, default)
        return float(v) if not pd.isna(v) else default
    except:
        return default

# Values
total_sales  = safe(s_row,  "Total Sales Value")
returns      = safe(s_row,  "Returns Value")
inv_disc     = safe(s_row,  "Invoice Discounts")
extra_disc   = 0.0
net_sales    = total_sales - returns - inv_disc - extra_disc

collection   = safe(op_row, "Total Collection")
overdue_val  = safe(ov_row, "Overdue Value")
total_bal    = safe(ov_row, "Total Balance")

tgt_year     = safe(tgt_row, "Full Year")
tgt_month    = safe(tgt_row, "Month")
tgt_quarter  = safe(tgt_row, "Quarter")
tgt_ytd      = safe(tgt_row, "YTD")

actual_year    = net_sales
actual_month   = actual_year * (current_month / 12)
actual_quarter = actual_year * (current_quarter / 4)
actual_ytd     = actual_year * (current_month / 12)

# =========================
# HEADER
# =========================
st.title(f"داشبورد أداء — {selected_label}")

# =========================
# SECTION 1: TARGET KPIs
# =========================
st.header("التارجت ونسبة التحقيق")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(kpi_card("تارجت السنة",     actual_year,    tgt_year or 1),    unsafe_allow_html=True)
with c2:
    st.markdown(kpi_card("تارجت الكوارتر",  actual_quarter, tgt_quarter or 1), unsafe_allow_html=True)
with c3:
    st.markdown(kpi_card("تارجت الشهر",     actual_month,   tgt_month or 1),   unsafe_allow_html=True)
with c4:
    st.markdown(kpi_card("Up to date (YTD)", actual_ytd,     tgt_ytd or 1),     unsafe_allow_html=True)

st.divider()

# =========================
# SECTION 2: SALES FLOW
# =========================
st.header("تحليل المبيعات")

col_flow, col_detail = st.columns([1, 1])

with col_flow:
    st.markdown("##### تدفق المبيعات")
    st.markdown(sales_flow_html(total_sales, returns, inv_disc, extra_disc),
                unsafe_allow_html=True)

with col_detail:
    st.markdown("##### ملخص المبيعات")
    st.markdown(f"""
| البند | القيمة |
|---|---|
| إجمالي المبيعات | {fmt(total_sales)} |
| مرتجعات البيع | {fmt(returns)} |
| بعد المرتجعات | {fmt(total_sales - returns)} |
| خصومات عادية | {fmt(inv_disc)} |
| خصومات إضافية | {fmt(extra_disc)} |
| **صافي المبيعات** | **{fmt(net_sales)}** |
""")

    st.markdown("##### التحصيل")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("إجمالي التحصيل", fmt(collection))
    with c2:
        st.metric("متأخرات +120 يوم", fmt(overdue_val))
    with c3:
        st.metric("الرصيد الكلي", fmt(total_bal))

st.divider()

# =========================
# SECTION 3: PRODUCTS TARGET
# =========================
st.header("أداء المنتجات")

tab1, tab2, tab3, tab4 = st.tabs(["السنة الكاملة", "الشهر", "الكوارتر", "YTD"])

def filter_products(df, col, val):
    if df.empty or col not in df.columns:
        return pd.DataFrame()
    return df[df[col] == val][["Product Name","Units","Value"]].reset_index(drop=True)

with tab1:
    df_p = filter_products(tgt_pipeline["products_full"], id_col, selected_id_num)
    if not df_p.empty:
        st.dataframe(df_p, use_container_width=True)
    else:
        st.info("لا توجد بيانات")

with tab2:
    df_p = filter_products(tgt_pipeline["products_month"], id_col, selected_id_num)
    if not df_p.empty:
        st.dataframe(df_p, use_container_width=True)
    else:
        st.info("لا توجد بيانات")

with tab3:
    df_p = filter_products(tgt_pipeline["products_quarter"], id_col, selected_id_num)
    if not df_p.empty:
        st.dataframe(df_p, use_container_width=True)
    else:
        st.info("لا توجد بيانات")

with tab4:
    df_p = filter_products(tgt_pipeline["products_ytd"], id_col, selected_id_num)
    if not df_p.empty:
        st.dataframe(df_p, use_container_width=True)
    else:
        st.info("لا توجد بيانات")

st.divider()

# =========================
# SECTION 4: RAW TABLES
# =========================
with st.expander("جدول المبيعات التفصيلي"):
    raw = sales_data.get("_raw", pd.DataFrame())
    if not raw.empty and id_col in raw.columns:
        st.dataframe(raw[raw[id_col] == selected_id_num], use_container_width=True)

with st.expander("جدول التحصيل التفصيلي"):
    op_df = opening_data.get(dict_key, pd.DataFrame())
    if not op_df.empty and id_col in op_df.columns:
        st.dataframe(op_df[op_df[id_col] == selected_id_num], use_container_width=True)

with st.expander("جدول المديونية التفصيلي"):
    ov_df = overdue_data.get(dict_key, pd.DataFrame())
    if not ov_df.empty and id_col in ov_df.columns:
        st.dataframe(ov_df[ov_df[id_col] == selected_id_num], use_container_width=True)
