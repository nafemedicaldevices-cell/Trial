import pandas as pd
import numpy as np

def process_sales(sales, mapping, codes):

    # =========================
    # CLEAN COLUMNS
    # =========================
    sales.columns = sales.columns.str.strip()

    sales.columns = [
        'Date','Warehouse Name','Client Code','Client Name','Notes','MF','Mostanad',
        'Rep Code','Sales Unit Before Edit','Returns Unit Before Edit',
        'Sales Price','Invoice Discounts','Sales Value',
    ]

    # =========================
    # OLD PRODUCT FIX
    # =========================
    for col in ['Old Product Code','Old Product Name']:
        if col not in sales.columns:
            sales[col] = None

    mask = sales['Date'].astype(str).str.strip() == "كود الصنف"

    sales.loc[mask,'Old Product Code'] = sales.loc[mask,'Warehouse Name']
    sales.loc[mask,'Old Product Name'] = sales.loc[mask,'Client Code']

    sales[['Old Product Code','Old Product Name']] = \
        sales[['Old Product Code','Old Product Name']].ffill()

    # =========================
    # FILTER ROWS
    # =========================
    sales = sales[
        sales['Date'].notna() &
        (sales['Date'].astype(str).str.strip() != '') &
        (~sales['Date'].astype(str).str.contains('المندوب|كود الفرع|تاريخ|كود الصنف', na=False))
    ].copy()

    # =========================
    # NUMERIC
    # =========================
    num_cols = [
        'Sales Unit Before Edit',
        'Returns Unit Before Edit',
        'Sales Price',
        'Invoice Discounts',
        'Sales Value'
    ]

    sales[num_cols] = sales[num_cols].apply(pd.to_numeric, errors='coerce').fillna(0)

    sales['Old Product Code'] = pd.to_numeric(sales['Old Product Code'], errors='coerce').astype('Int64')
    sales['Rep Code'] = pd.to_numeric(sales['Rep Code'], errors='coerce').astype('Int64')

    # =========================
    # MERGE
    # =========================
    if mapping is not None:
        sales = sales.merge(mapping, on='Old Product Code', how='left')

    if codes is not None:
        codes['Rep Code'] = pd.to_numeric(codes['Rep Code'], errors='coerce').astype('Int64')
        sales = sales.merge(codes, on='Rep Code', how='left')

    # =========================
    # CALCULATIONS
    # =========================
    sales['Total Sales Value'] = sales['Sales Unit Before Edit'] * sales['Sales Price']
    sales['Returns Value'] = sales['Returns Unit Before Edit'] * sales['Sales Price']
    sales['Sales After Returns'] = sales['Total Sales Value'] - sales['Returns Value']

    sales['Net Sales Unit Before Edit'] = (
        sales['Sales Unit Before Edit'] - sales['Returns Unit Before Edit']
    )

    sales['Net Sales Unit'] = sales['Net Sales Unit Before Edit']

    # =========================
    # GROUP FUNCTION
    # =========================
    def group_and_format(df, group_cols, sum_cols):
        group_cols = [c for c in group_cols if c in df.columns]
        return df.groupby(group_cols, as_index=False)[sum_cols].sum()

    # =========================
    # OUTPUTS
    # =========================
    result = {}

    result["rep_client"] = group_and_format(
        sales,
        ['Rep Code','Client Code','Client Name'],
        ['Total Sales Value','Returns Value','Sales After Returns','Invoice Discounts']
    )

    result["manager_client"] = group_and_format(
        sales,
        ['Manager Code','Client Code','Client Name'],
        ['Total Sales Value','Returns Value','Sales After Returns','Invoice Discounts']
    )

    result["area_client"] = group_and_format(
        sales,
        ['Area Code','Client Code','Client Name'],
        ['Total Sales Value','Returns Value','Sales After Returns','Invoice Discounts']
    )

    result["rep_value"] = group_and_format(
        sales,
        ['Rep Code'],
        ['Total Sales Value','Returns Value','Sales After Returns','Invoice Discounts']
    )

    result["manager_value"] = group_and_format(
        sales,
        ['Manager Code'],
        ['Total Sales Value','Returns Value','Sales After Returns','Invoice Discounts']
    )

    result["area_value"] = group_and_format(
        sales,
        ['Area Code'],
        ['Total Sales Value','Returns Value','Sales After Returns','Invoice Discounts']
    )

    result["rep_products"] = group_and_format(
        sales,
        ['Rep Code','Product Code','Product Name'],
        ['Sales Value','Net Sales Unit']
    )

    result["manager_products"] = group_and_format(
        sales,
        ['Manager Code','Product Code','Product Name'],
        ['Sales Value','Net Sales Unit']
    )

    result["area_products"] = group_and_format(
        sales,
        ['Area Code','Product Code','Product Name'],
        ['Sales Value','Net Sales Unit']
    )

    return result
