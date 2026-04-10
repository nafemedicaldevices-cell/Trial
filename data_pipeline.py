import pandas as pd

# =========================
# 📅 TIME SETTINGS
# =========================
current_month = pd.Timestamp.today().month
current_quarter = (current_month - 1) // 3 + 1
past_quarters = max(current_quarter - 1, 0)


# =========================
# 📂 LOAD DATA
# =========================
def load_data():
    return {
        "sales": pd.read_excel("Sales.xlsx"),
        "overdue": pd.read_excel("Overdue.xlsx"),
        "extra_discounts": pd.read_excel("Extradiscounts.xlsx"),
        "opening": pd.read_excel("Opening.xlsx"),
        "opening_detail": pd.read_excel("Opening Detail.xlsx"),

        "target_manager": pd.read_excel("Target Manager.xlsx"),
        "target_area": pd.read_excel("Target Area.xlsx"),
        "target_rep": pd.read_excel("Target Rep.xlsx"),
        "target_supervisor": pd.read_excel("Target Supervisor.xlsx"),
        "target_evak": pd.read_excel("Target Evak.xlsx"),

        "mapping": pd.read_excel("Mapping.xlsx"),
        "codes": pd.read_excel("Code.xlsx")
    }


# =========================
# 🚀 PIPELINE
# =========================
def build_target_pipeline(df, id_name, mapping):

    df = df.copy()
    mapping = mapping.copy()

    df.columns = df.columns.str.strip()

    fixed_cols = [c for c in ["Year", "Product Code", "Old Product Name", "Sales Price"] if c in df.columns]
    dynamic_cols = [c for c in df.columns if c not in fixed_cols]

    # 🔄 reshape
    df = df.melt(
        id_vars=fixed_cols,
        value_vars=dynamic_cols,
        var_name=id_name,
        value_name="Target (Unit)"
    )

    # 🧹 clean IDs
    df[id_name] = pd.to_numeric(
        df[id_name].astype(str).str.replace(r"[^0-9]", "", regex=True),
        errors="coerce"
    )

    df["Product Code"] = pd.to_numeric(df["Product Code"], errors="coerce")
    mapping["Product Code"] = pd.to_numeric(mapping["Product Code"], errors="coerce")

    mapping = mapping.drop_duplicates("Product Code")

    # 🔗 merge
    df = df.merge(mapping, on="Product Code", how="left")

    # 🔢 numeric
    df["Target (Unit)"] = pd.to_numeric(df["Target (Unit)"], errors="coerce").fillna(0)
    df["Sales Price"] = pd.to_numeric(df["Sales Price"], errors="coerce").fillna(0)

    # 💰 value
    df["Full Value"] = df["Target (Unit)"] * df["Sales Price"]

    # =========================
    # 📊 KPI CALCULATION
    # =========================
    full = df.copy()
    full["Value"] = full["Full Value"]

    month = df.copy()
    month["Value"] = full["Full Value"] * (current_month / 12)

    quarter = df.copy()
    quarter["Value"] = full["Full Value"] * (past_quarters / 4)

    ytd = df.copy()
    ytd["Value"] = full["Full Value"] * (current_month / 12)

    # =========================
    # 📊 VALUE TABLE
    # =========================
    def group(d):
        return d.groupby([id_name], as_index=False)["Value"].sum()

    value_table = group(full).rename(columns={"Value": "Full Year 🏆"})
    value_table["Month 📅"] = group(month)["Value"]
    value_table["Quarter 📊"] = group(quarter)["Value"]
    value_table["YTD 📈"] = group(ytd)["Value"]

    # =========================
    # 📦 PRODUCTS TABLE
    # =========================
    def product_group(d):
        return d.groupby(
            [id_name, "Product Code", "Product Name"],
            as_index=False
        ).agg(
            Units=("Target (Unit)", "sum"),
            Value=("Value", "sum")
        )

    return {
        "value_table": value_table,
        "products_full": product_group(full),
        "products_month": product_group(month),
        "products_quarter": product_group(quarter),
        "products_ytd": product_group(ytd),
    }

#---------------------------------------------------------------------------------------------------------------------------------------------------------
# Sales
#---------------------------------------------------------------------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np

# =========================
# 📊 SALES PIPELINE CLEAN
# =========================
def build_sales_pipeline(sales, mapping, codes):

    sales = sales.copy()
    mapping = mapping.copy()
    codes = codes.copy()

    # =========================
    # 🧹 CLEAN COLUMNS
    # =========================
    sales.columns = sales.columns.str.strip()

    expected_cols = [
        'Date','Warehouse Name','Client Code','Client Name','Notes','MF','Mostanad',
        'Rep Code','Sales Unit Before Edit','Returns Unit Before Edit',
        'Sales Price','Invoice Discounts','Sales Value'
    ]

    if len(sales.columns) == len(expected_cols):
        sales.columns = expected_cols

    # =========================
    # 🔢 FIX TYPES
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

    # =========================
    # 🧠 FIX PRODUCT HEADER ROWS (important)
    # =========================
    for col in ['Old Product Code', 'Old Product Name']:
        if col not in sales.columns:
            sales[col] = np.nan
        sales[col] = sales[col].astype('object')

    if 'Date' in sales.columns:
        mask = sales['Date'].astype(str).str.strip().eq("كود الصنف")

        sales.loc[mask, 'Old Product Code'] = sales.loc[mask, 'Warehouse Name']
        sales.loc[mask, 'Old Product Name'] = sales.loc[mask, 'Client Code']

        sales[['Old Product Code','Old Product Name']] = sales[
            ['Old Product Code','Old Product Name']
        ].ffill()

    # =========================
    # 🧹 FILTER CLEAN ROWS
    # =========================
    if 'Date' in sales.columns:
        drop_keywords = 'المندوب|كود الفرع|تاريخ|كود الصنف'
        sales = sales[sales['Date'].notna()]
        sales = sales[~sales['Date'].astype(str).str.contains(drop_keywords, na=False)]

    # =========================
    # 🔢 FINAL NUMERIC CLEAN
    # =========================
    sales['Old Product Code'] = pd.to_numeric(sales['Old Product Code'], errors='coerce')
    sales['Rep Code'] = pd.to_numeric(sales['Rep Code'], errors='coerce')

    # =========================
    # 🔗 MERGE MAPPING
    # =========================
    mapping_cols = [
        'Old Product Code','4 Classification','Product Name',
        'Product Code','Category','Next Factor','2 Classification'
    ]
    mapping_cols = [c for c in mapping_cols if c in mapping.columns]

    sales = sales.merge(mapping[mapping_cols], on='Old Product Code', how='left')

    sales['Next Factor'] = sales['Next Factor'].fillna(1)

    # =========================
    # 🔗 MERGE CODES
    # =========================
    sales = sales.merge(codes, on='Rep Code', how='left')

    # =========================
    # 💰 KPI CALCULATION
    # =========================
    sales['Total Sales Value'] = sales['Sales Unit Before Edit'] * sales['Sales Price']
    sales['Returns Value'] = sales['Returns Unit Before Edit'] * sales['Sales Price']

    sales['Net Sales Value'] = sales['Total Sales Value'] - sales['Returns Value']

    sales['Net Units'] = (
        sales['Sales Unit Before Edit'] - sales['Returns Unit Before Edit']
    ) * sales['Next Factor']

    # =========================
    # 📊 SAFE GROUP ENGINE
    # =========================
    def safe_group(df, group_cols, sum_cols):
        group_cols = [c for c in group_cols if c in df.columns]
        sum_cols = [c for c in sum_cols if c in df.columns]

        if not group_cols:
            return pd.DataFrame()

        return df.groupby(group_cols, as_index=False)[sum_cols].sum()

    # =========================
    # 📦 OUTPUT LEVELS
    # =========================
    return {

        # 👨‍💼 REP
        "rep_value": safe_group(
            sales,
            ['Rep Code'],
            ['Total Sales Value','Returns Value','Net Sales Value','Net Units']
        ),
        "rep_products": safe_group(
            sales,
            ['Rep Code','Product Code','Product Name'],
            ['Net Sales Value','Net Units']
        ),

        # 🏢 MANAGER
        "manager_value": safe_group(
            sales,
            ['Manager Code'],
            ['Total Sales Value','Returns Value','Net Sales Value','Net Units']
        ),
        "manager_products": safe_group(
            sales,
            ['Manager Code','Product Code','Product Name'],
            ['Net Sales Value','Net Units']
        ),

        # 🌍 AREA
        "area_value": safe_group(
            sales,
            ['Area Code'],
            ['Total Sales Value','Returns Value','Net Sales Value','Net Units']
        ),
        "area_products": safe_group(
            sales,
            ['Area Code','Product Code','Product Name'],
            ['Net Sales Value','Net Units']
        ),

        # 🧑‍💼 SUPERVISOR
        "supervisor_value": safe_group(
            sales,
            ['Supervisor Code'],
            ['Total Sales Value','Returns Value','Net Sales Value','Net Units']
        ),

        # 📦 RAW
        "raw": sales
    }
