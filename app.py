#-------------------------------------------------------------------------------------
# Sales
#-------------------------------------------------------------------------------------
import pandas as pd
import numpy as np

# تنظيف أسماء الأعمدة
sales.columns = sales.columns.str.strip()
sales.columns = [
    'Date','Warehouse Name','Client Code','Client Name','Notes','MF','Mostanad',
    'Rep Code','Sales Unit Before Edit','Returns Unit Before Edit',
    'Sales Price','Invoice Discounts','Sales Value',
]

# التأكد من وجود الأعمدة المطلوبة
for col in ['Old Product Code','Old Product Name']:
    if col not in sales.columns:
        sales[col] = None

# معالجة الصفوف التي تحتوي على عناوين أو كود الصنف
mask = sales['Date'].astype(str).str.strip() == "كود الصنف"
sales.loc[mask,'Old Product Code'] = sales.loc[mask,'Warehouse Name']
sales.loc[mask,'Old Product Name'] = sales.loc[mask,'Client Code']
sales[['Old Product Code','Old Product Name']] = sales[['Old Product Code','Old Product Name']].ffill()

# فلترة الصفوف الفارغة أو عناوين غير مرغوب فيها
sales = sales[
    sales['Date'].notna() &
    (sales['Date'].astype(str).str.strip() != '') &
    (~sales['Date'].astype(str).str.contains('المندوب|كود الفرع|تاريخ|كود الصنف', na=False))
].copy()

# تحويل الأعمدة الرقمية
num_cols = [
    'Sales Unit Before Edit','Returns Unit Before Edit',
    'Sales Price','Invoice Discounts','Sales Value'
]
sales[num_cols] = sales[num_cols].apply(pd.to_numeric, errors='coerce').fillna(0)

sales['Old Product Code'] = pd.to_numeric(sales['Old Product Code'], errors='coerce').astype('Int64')
sales['Rep Code'] = pd.to_numeric(sales['Rep Code'], errors='coerce').astype('Int64')

# دمج Mapping
sales = sales.merge(
    mapping[['Old Product Code','4 Classification','Product Name','Product Code','Category','Next Factor','2 Classification']],
    on='Old Product Code',
    how='left'
)

# ملء Next Factor إذا كان فارغ
sales['Next Factor'] = sales.get('Next Factor', 1).fillna(1)

# دمج Codes
codes['Rep Code'] = pd.to_numeric(codes['Rep Code'], errors='coerce').astype('Int64')
sales = sales.merge(codes, on='Rep Code', how='left')

# حسابات مباشرة بدون GroupBy
sales['Total Sales Value'] = sales['Sales Unit Before Edit'] * sales['Sales Price']
sales['Returns Value'] = sales['Returns Unit Before Edit'] * sales['Sales Price']
sales['Sales After Returns'] = sales['Total Sales Value'] - sales['Returns Value']
sales['Net Sales Unit Before Edit'] = sales['Sales Unit Before Edit'] - sales['Returns Unit Before Edit']
sales['Net Sales Unit'] = sales['Net Sales Unit Before Edit'] * sales['Next Factor']
