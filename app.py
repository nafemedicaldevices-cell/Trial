import pandas as pd

# =========================
# LOAD DATA 🔥
# =========================
opening = pd.read_excel("Opening.xlsx")
codes = pd.read_excel("Code.xlsx")

# =========================
# COLUMN STANDARDIZATION
# =========================
opening = opening.copy()

opening.columns = [
    'Branch',"Evak",'Opening Balance','Total Sales After Invoice Discounts',
    'Returns','Sales Value Before Extra Discounts',
    'Cash Collection','Collection Checks',
    'Returned Chick','Collection Returned Chick',
    "Extra Discounts",'Daienah','End Balance'
]

# =========================
# FIX DTYPE
# =========================
opening['Rep Code'] = pd.Series(dtype='object')
opening['Old Rep Name'] = pd.Series(dtype='object')

# =========================
# 🔥 EXTRACT REP INFO
# =========================
mask = opening['Branch'].astype(str).str.strip().eq("كود المندوب")

opening.loc[mask, 'Rep Code'] = opening.loc[mask, 'Opening Balance'].astype('object')
opening.loc[mask, 'Old Rep Name'] = opening.loc[mask, 'Total Sales After Invoice Discounts'].astype('object')

opening[['Rep Code','Old Rep Name']] = opening[['Rep Code','Old Rep Name']].ffill()

# =========================
# 🔥 FILTER VALID ROWS
# =========================
opening = opening[
    opening['Branch'].notna() &
    (opening['Branch'].astype(str).str.strip() != '') &
    (~opening['Branch'].astype(str).str.contains(
        'نسبة المندوب|كود المندوب|اجماليات|كود الفرع',
        na=False
    ))
].copy()

# =========================
# NUMERIC CONVERSION
# =========================
num_cols = [
    'Opening Balance','Total Sales After Invoice Discounts','Returns',
    'Sales Value Before Extra Discounts',
    'Cash Collection','Collection Checks',
    'Returned Chick','Collection Returned Chick',
    'Extra Discounts','Daienah','End Balance'
]

for col in num_cols:
    opening[col] = pd.to_numeric(opening[col], errors='coerce').fillna(0)

# =========================
# KPI CALCULATIONS
# =========================
opening['Total Collection'] = opening['Cash Collection'] + opening['Collection Checks']

opening['Sales After Returns'] = (
    opening['Total Sales After Invoice Discounts'] - opening['Returns']
)

# =========================
# CLEAN REP CODE
# =========================
opening['Rep Code'] = pd.to_numeric(opening['Rep Code'], errors='coerce').astype('Int64')

# =========================
# MERGE CODES
# =========================
codes['Rep Code'] = pd.to_numeric(codes['Rep Code'], errors='coerce').astype('Int64')

opening = opening.merge(codes, on='Rep Code', how='left')

# =========================
# 🔥 FINAL CLEAN BEFORE GROUP
# =========================
opening_clean = opening[
    opening['Rep Code'].notna()
].copy()

# =========================
# SAFE GROUP ENGINE
# =========================
def safe_group(df, group_cols, sum_cols):
    group_cols = [c for c in group_cols if c in df.columns]
    sum_cols = [c for c in sum_cols if c in df.columns]

    return df.groupby(group_cols, as_index=False)[sum_cols].sum()

# =========================
# GROUP CONFIG
# =========================
OPENING_GROUPS = {
    "rep_value": {
        "group": ["Rep Code"],
        "sum": ["Opening Balance","Cash Collection","Collection Checks","Extra Discounts","End Balance"]
    },
    "manager_value": {
        "group": ["Manager Code"],
        "sum": ["Opening Balance","Cash Collection","Collection Checks","Extra Discounts","End Balance"]
    },
    "area_value": {
        "group": ["Area Code"],
        "sum": ["Opening Balance","Cash Collection","Collection Checks","Extra Discounts","End Balance"]
    },
    "supervisor_value": {
        "group": ["Supervisor Code"],
        "sum": ["Opening Balance","Cash Collection","Collection Checks","Extra Discounts","End Balance"]
    }
}

# =========================
# RUN ALL GROUPS
# =========================
opening_results = {}

for name, cfg in OPENING_GROUPS.items():
    opening_results[name] = safe_group(
        opening_clean,
        cfg["group"],
        cfg["sum"]
    )

# =========================
# OUTPUTS
# =========================
opening_rep_value = opening_results["rep_value"]
opening_manager_value = opening_results["manager_value"]
opening_area_value = opening_results["area_value"]
opening_supervisor_value = opening_results["supervisor_value"]
