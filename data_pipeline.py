import pandas as pd
import numpy as np

# =========================
# GLOBAL SETTINGS
# =========================
pd.set_option('future.no_silent_downcasting', True)
current_month = pd.Timestamp.today().month


# =========================
# LOAD DATA
# =========================
def load_data():
    sales = pd.read_excel("Sales.xlsx")
    overdue = pd.read_excel("Overdue.xlsx")
    extra_discounts = pd.read_excel("Extradiscounts.xlsx")
    opening = pd.read_excel("Opening.xlsx")
    opening_detail = pd.read_excel("Opening Detail.xlsx")

    target_manager = pd.read_excel("Target Manager.xlsx")
    target_area = pd.read_excel("Target Area.xlsx")
    target_rep = pd.read_excel("Target Rep.xlsx")

    mapping = pd.read_excel("Mapping.xlsx")
    codes = pd.read_excel("Code.xlsx")

    return (
        sales, overdue, extra_discounts,
        opening, opening_detail,
        target_manager, target_area, target_rep,
        mapping, codes
    )


# =========================
# TARGET PIPELINE
# =========================
def build_target_pipeline(file_name, id_name, mapping):

    df = pd.read_excel(file_name)

    df.columns = df.columns.str.strip().str.replace(r'\s+', ' ', regex=True)

    fixed_cols = ["Year", "Product Code", "Old Product Name", "Sales Price"]
    dynamic_cols = [c for c in df.columns if c not in fixed_cols]

    df = df.melt(
        id_vars=fixed_cols,
        value_vars=dynamic_cols,
        var_name=id_name,
        value_name="Target (Unit)"
    )

    df[id_name] = pd.to_numeric(
        df[id_name].astype(str).str.replace(r'[^0-9]', '', regex=True),
        errors='coerce'
    )

    df["Product Code"] = pd.to_numeric(df["Product Code"], errors='coerce')

    mapping_clean = mapping.copy()
    mapping_clean["Product Code"] = pd.to_numeric(mapping_clean["Product Code"], errors='coerce')

    df = df.merge(
        mapping_clean[["Product Code","Product Name","2 Classification","Category"]],
        on="Product Code",
        how="left"
    )

    df["Full Target Value"] = df["Target (Unit)"] * df["Sales Price"]

    def add_factor(base, factor):
        temp = base.copy()
        temp["Target (Value)"] = (temp["Full Target Value"] / 12) * factor
        return temp

    df_full = add_factor(df, 12)
    df_month = add_factor(df, 1)
    df_quarter = add_factor(df, 3)
    df_ytd = add_factor(df, current_month)

    def group(df_in):
        return df_in.groupby([id_name], as_index=False)["Target (Value)"].sum()

    def group_products(df_in):
        return df_in.groupby(
            [
                id_name,"2 Classification","Category",
                "Product Code","Product Name",
                "Target (Unit)","Sales Price"
            ],
            as_index=False
        )["Target (Value)"].sum()

    return {
        "full": df,
        "value_full": group(df_full),
        "value_month": group(df_month),
        "value_quarter": group(df_quarter),
        "value_uptodate": group(df_ytd),

        "products_full": group_products(df_full),
        "products_month": group_products(df_month),
        "products_quarter": group_products(df_quarter),
        "products_uptodate": group_products(df_ytd),
    }


# =========================
# SALES CLEANING
# =========================
def clean_sales(sales, mapping, codes):

    sales.columns = sales.columns.str.strip()

    sales = sales.merge(mapping, on="Old Product Code", how="left")
    sales = sales.merge(codes, on="Rep Code", how="left")

    sales["Total Sales Value"] = sales["Sales Unit Before Edit"] * sales["Sales Price"]
    sales["Returns Value"] = sales["Returns Unit Before Edit"] * sales["Sales Price"]
    sales["Sales After Returns"] = sales["Total Sales Value"] - sales["Returns Value"]

    return sales


# =========================
# OVERDUE CLEANING
# =========================
def clean_overdue(overdue):

    overdue = overdue.iloc[:, :9].copy()

    overdue.columns = [
        "Client Name","Client Code","15 Days","30 Days","60 Days","90 Days",
        "120 Days","More Than 120 Days","Balance"
    ]

    overdue["Overdue"] = overdue["120 Days"] + overdue["More Than 120 Days"]

    return overdue


# =========================
# OPENING CLEANING
# =========================
def clean_opening(opening):

    opening.columns = [
        'Branch',"Evak",'Opening Balance','Total Sales After Invoice Discounts',
        'Returns','Sales Value Before Extra Discounts',
        'Cash Collection','Collection Checks',
        'Returned Chick','Collection Returned Chick',
        "Extra Discounts",'Daienah','End Balance'
    ]

    opening["Sales After Returns"] = (
        opening["Total Sales After Invoice Discounts"] - opening["Returns"]
    )

    opening["Total Collection"] = (
        opening["Cash Collection"] + opening["Collection Checks"]
    )

    return opening


# =========================
# OPENING DETAIL CLEANING
# =========================
def clean_opening_detail(opening_detail, codes):

    opening_detail = opening_detail.iloc[:, :11].copy()

    opening_detail.columns = [
        'Client Code',"Client Name",'Opening Balance',
        'Total Sales After Invoice Discounts','Returns',
        'Extra Discounts','Total Collection',"Madfoaat",
        'Tasweyat Daiinah',"End Balance",
        'Motalbet El Fatrah'
    ]

    opening_detail["Rep Code"] = np.nan
    opening_detail["Old Rep Name"] = np.nan

    mask = opening_detail['Client Code'].astype(str).str.strip().eq("كود الفرع")

    opening_detail.loc[mask, 'Rep Code'] = opening_detail.loc[mask, 'Returns']
    opening_detail.loc[mask, 'Old Rep Name'] = opening_detail.loc[mask, 'Extra Discounts']

    opening_detail[['Rep Code','Old Rep Name']] = opening_detail[['Rep Code','Old Rep Name']].ffill()

    opening_detail["Rep Code"] = pd.to_numeric(opening_detail["Rep Code"], errors='coerce')

    opening_detail = opening_detail[
        opening_detail['Client Code'].notna() &
        (opening_detail['Client Code'].astype(str).str.strip() != '') &
        (~opening_detail['Client Code'].astype(str).str.contains(
            "كود الفرع|كود العميل",
            na=False
        ))
    ].copy()

    opening_detail = opening_detail.merge(codes, on="Rep Code", how="left")

    opening_detail["Sales After Returns"] = (
        opening_detail["Total Sales After Invoice Discounts"] -
        opening_detail["Returns"]
    )

    return opening_detail


# =========================
# MAIN PIPELINE
# =========================
def run_pipeline():

    (
        sales, overdue, extra_discounts,
        opening, opening_detail,
        target_manager, target_area, target_rep,
        mapping, codes
    ) = load_data()

    sales = clean_sales(sales, mapping, codes)
    overdue = clean_overdue(overdue)
    opening = clean_opening(opening)
    opening_detail = clean_opening_detail(opening_detail, codes)

    rep = build_target_pipeline("Target Rep.xlsx", "Rep Code", mapping)
    manager = build_target_pipeline("Target Manager.xlsx", "Manager Code", mapping)
    area = build_target_pipeline("Target Area.xlsx", "Area Code", mapping)

    return {
        "sales": sales,
        "overdue": overdue,
        "opening": opening,
        "opening_detail": opening_detail,
        "rep": rep,
        "manager": manager,
        "area": area
    }