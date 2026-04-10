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
        "target_evak": pd.read_excel("Target Evak.xlsx"),
    }


# =========================
# 💰 SALES CLEAN ONLY (NO MERGE YET)
# =========================
def build_sales_pipeline(sales, mapping, codes):

    df = sales.copy()
    df.columns = df.columns.str.strip()

    expected_cols = [
        'Date','Warehouse Name','Client Code','Client Name','Notes','MF','Mostanad',
        'Rep Code','Sales Unit Before Edit','Returns Unit Before Edit',
        'Sales Price','Invoice Discounts','Sales Value'
    ]

    if len(df.columns) == len(expected_cols):
        df.columns = expected_cols

    # numeric
    num_cols = [
        'Sales Unit Before Edit',
        'Returns Unit Before Edit',
        'Sales Price',
        'Invoice Discounts'
    ]

    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    # product header fix
    if 'Date' in df.columns:
        mask = df['Date'].astype(str).str.strip().eq("كود الصنف")

        df.loc[mask, 'Old Product Code'] = df.loc[mask, 'Warehouse Name']
        df.loc[mask, 'Old Product Name'] = df.loc[mask, 'Client Code']

        df[['Old Product Code','Old Product Name']] = df[
            ['Old Product Code','Old Product Name']
        ].ffill()

    # calculations
    df['Total Sales Value'] = df['Sales Unit Before Edit'] * df['Sales Price']
    df['Returns Value'] = df['Returns Unit Before Edit'] * df['Sales Price']
    df['Sales After Returns'] = df['Total Sales Value'] - df['Returns Value']

    return df


# =========================
# 🎯 TARGET CLEAN ONLY
# =========================
def build_target_pipeline(target_df, key_col):

    df = target_df.copy()
    df.columns = df.columns.str.strip()

    if key_col in df.columns:
        df[key_col] = df[key_col].astype(str)

    num_cols = [c for c in df.columns if "Target" in c]
    df[num_cols] = df[num_cols].apply(pd.to_numeric, errors="coerce").fillna(0)

    return df
