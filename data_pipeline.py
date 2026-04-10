import pandas as pd
import numpy as np


# =========================
# 📥 LOAD DATA
# =========================
def load_data():
    return {
        "sales": pd.read_excel("Sales.xlsx"),
        "mapping": pd.read_excel("Mapping.xlsx"),
        "codes": pd.read_excel("Code.xlsx"),

        "target_rep": pd.read_excel("Target Rep.xlsx"),
        "target_manager": pd.read_excel("Target Manager.xlsx"),
        "target_area": pd.read_excel("Target Area.xlsx"),
        "target_supervisor": pd.read_excel("Target Supervisor.xlsx"),
    }


# =========================
# 💰 SALES PIPELINE
# =========================
def build_sales_pipeline(sales, mapping, codes):

    sales = sales.copy()
    sales.columns = sales.columns.str.strip()

    expected_cols = [
        'Date','Warehouse Name','Client Code','Client Name','Notes','MF','Mostanad',
        'Rep Code','Sales Unit Before Edit','Returns Unit Before Edit',
        'Sales Price','Invoice Discounts','Sales Value'
    ]

    if len(sales.columns) == len(expected_cols):
        sales.columns = expected_cols


    # =========================
    # 📦 PRODUCT HEADER FIX
    # =========================
    if 'Date' in sales.columns:

        mask = sales['Date'].astype(str).str.strip().eq("كود الصنف")

        if 'Old Product Code' not in sales.columns:
            sales['Old Product Code'] = np.nan
        if 'Old Product Name' not in sales.columns:
            sales['Old Product Name'] = np.nan

        sales['Old Product Code'] = sales['Old Product Code'].astype('object')
        sales['Old Product Name'] = sales['Old Product Name'].astype('object')

        sales.loc[mask, 'Old Product Code'] = sales.loc[mask, 'Warehouse Name'].astype(str)
        sales.loc[mask, 'Old Product Name'] = sales.loc[mask, 'Client Code'].astype(str)

        sales[['Old Product Code','Old Product Name']] = sales[
            ['Old Product Code','Old Product Name']
        ].ffill()


    # =========================
    # 🧹 FILTER
    # =========================
    drop_keywords = 'المندوب|كود الفرع|تاريخ|كود الصنف'

    sales = sales[sales['Date'].notna()].copy()
    sales = sales[~sales['Date'].astype(str).str.contains(drop_keywords, na=False)].copy()


    # =========================
    # 🔢 NUMERIC
    # =========================
    num_cols = [
        'Sales Unit Before Edit',
        'Returns Unit Before Edit',
        'Sales Price',
        'Invoice Discounts',
        'Sales Value'
    ]

    for col in num_cols:
        if col in sales.columns:
            sales[col] = pd.to_numeric(sales[col], errors='coerce').fillna(0)


    if 'Old Product Code' in sales.columns:
        sales['Old Product Code'] = pd.to_numeric(sales['Old Product Code'], errors='coerce').astype('Int64')

    if 'Rep Code' in sales.columns:
        sales['Rep Code'] = pd.to_numeric(sales['Rep Code'], errors='coerce').astype('Int64')


    # =========================
    # 🧩 MAPPING
    # =========================
    if 'Old Product Code' in sales.columns:

        mapping_cols = [
            'Old Product Code','4 Classification','Product Name',
            'Product Code','Category','Next Factor','2 Classification'
        ]

        mapping_cols = [c for c in mapping_cols if c in mapping.columns]

        sales = sales.merge(mapping[mapping_cols], on='Old Product Code', how='left')


    # =========================
    # 🧩 CODES
    # =========================
    if 'Next Factor' not in sales.columns:
        sales['Next Factor'] = 1

    sales['Next Factor'] = sales['Next Factor'].fillna(1)

    codes['Rep Code'] = pd.to_numeric(codes['Rep Code'], errors='coerce').astype('Int64')

    sales = sales.merge(codes, on='Rep Code', how='left')


    # =========================
    # 💰 CALCULATIONS
    # =========================
    sales['Total Sales Value'] = sales['Sales Unit Before Edit'] * sales['Sales Price']
    sales['Returns Value'] = sales['Returns Unit Before Edit'] * sales['Sales Price']
    sales['Sales After Returns'] = sales['Total Sales Value'] - sales['Returns Value']

    sales['Net Sales Unit'] = (
        (sales['Sales Unit Before Edit'] - sales['Returns Unit Before Edit'])
        * sales['Next Factor']
    )


    # =========================
    # 📊 GROUP ENGINE
    # =========================
    def safe_group(df, group_cols, sum_cols):

        group_cols = [c for c in group_cols if c in df.columns]
        sum_cols = [c for c in sum_cols if c in df.columns]

        if not group_cols:
            return pd.DataFrame(columns=sum_cols)

        return df.groupby(group_cols, as_index=False)[sum_cols].sum()


    GROUP_DEFS = {
        "rep_value": {
            "group": ['Rep Code'],
            "sum": ['Total Sales Value','Returns Value','Sales After Returns','Invoice Discounts']
        },
        "manager_value": {
            "group": ['Manager Code'],
            "sum": ['Total Sales Value','Returns Value','Sales After Returns','Invoice Discounts']
        },
        "area_value": {
            "group": ['Area Code'],
            "sum": ['Total Sales Value','Returns Value','Sales After Returns','Invoice Discounts']
        },
        "supervisor_value": {
            "group": ['Supervisor Code'],
            "sum": ['Total Sales Value','Returns Value','Sales After Returns','Invoice Discounts']
        },
        "rep_products": {
            "group": ['Rep Code','Product Code','Product Name'],
            "sum": ['Sales Value','Net Sales Unit']
        },
        "manager_products": {
            "group": ['Manager Code','Product Code','Product Name'],
            "sum": ['Sales Value','Net Sales Unit']
        },
        "area_products": {
            "group": ['Area Code','Product Code','Product Name'],
            "sum": ['Sales Value','Net Sales Unit']
        }
    }


    results = {}
    for name, cfg in GROUP_DEFS.items():
        results[name] = safe_group(sales, cfg["group"], cfg["sum"])

    return results


# =========================
# 🎯 TARGET PIPELINE
# =========================
def build_target_pipeline(target_df, key_col):

    df = target_df.copy()
    df.columns = df.columns.str.strip()

    if key_col in df.columns:
        df[key_col] = pd.to_numeric(df[key_col], errors='coerce').astype('Int64')

    num_cols = [c for c in df.columns if "Target" in c]

    df[num_cols] = df[num_cols].apply(pd.to_numeric, errors='coerce').fillna(0)

    return df
