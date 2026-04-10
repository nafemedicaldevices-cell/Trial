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
# 🧹 CLEAN SALES ONLY
# =========================
def clean_sales(df):

    df = df.copy()
    df.columns = df.columns.str.strip()

    # ---------- expected structure fix ----------
    expected_cols = [
        'Date','Warehouse Name','Client Code','Client Name','Notes','MF','Mostanad',
        'Rep Code','Sales Unit Before Edit','Returns Unit Before Edit',
        'Sales Price','Invoice Discounts','Sales Value'
    ]

    if len(df.columns) == len(expected_cols):
        df.columns = expected_cols

    # ---------- numeric cleanup ----------
    num_cols = [
        'Sales Unit Before Edit',
        'Returns Unit Before Edit',
        'Sales Price',
        'Invoice Discounts'
    ]

    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    # ---------- product header fix ----------
    if 'Date' in df.columns:

        mask = df['Date'].astype(str).str.strip().eq("كود الصنف")

        if 'Old Product Code' not in df.columns:
            df['Old Product Code'] = np.nan
        if 'Old Product Name' not in df.columns:
            df['Old Product Name'] = np.nan

        df.loc[mask, 'Old Product Code'] = df.loc[mask, 'Warehouse Name']
        df.loc[mask, 'Old Product Name'] = df.loc[mask, 'Client Code']

        df[['Old Product Code','Old Product Name']] = df[
            ['Old Product Code','Old Product Name']
        ].ffill()

    # ---------- remove junk rows ----------
    drop_keywords = 'المندوب|كود الفرع|تاريخ|كود الصنف'

    if 'Date' in df.columns:
        df = df[df['Date'].notna()]
        df = df[~df['Date'].astype(str).str.contains(drop_keywords, na=False)]

    # ---------- numeric conversion ----------
    if 'Rep Code' in df.columns:
        df['Rep Code'] = pd.to_numeric(df['Rep Code'], errors='coerce')

    if 'Old Product Code' in df.columns:
        df['Old Product Code'] = pd.to_numeric(df['Old Product Code'], errors='coerce')

    # ---------- calculations ----------
    if all(c in df.columns for c in ['Sales Unit Before Edit','Sales Price']):
        df['Total Sales Value'] = df['Sales Unit Before Edit'] * df['Sales Price']

    if all(c in df.columns for c in ['Returns Unit Before Edit','Sales Price']):
        df['Returns Value'] = df['Returns Unit Before Edit'] * df['Sales Price']

    if 'Total Sales Value' in df.columns and 'Returns Value' in df.columns:
        df['Sales After Returns'] = df['Total Sales Value'] - df['Returns Value']

    return df


# =========================
# 🧹 CLEAN TARGET ONLY
# =========================
def clean_target(df, key_col):

    df = df.copy()
    df.columns = df.columns.str.strip()

    if key_col in df.columns:
        df[key_col] = df[key_col].astype(str)

    # numeric only for target columns
    target_cols = [c for c in df.columns if "Target" in c]

    for c in target_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    return df
