import pandas as pd
import numpy as np

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
        "opening": pd.read_excel("Opening.xlsx"),

        "target_manager": pd.read_excel("Target Manager.xlsx"),
        "target_area": pd.read_excel("Target Area.xlsx"),
        "target_rep": pd.read_excel("Target Rep.xlsx"),
        "target_supervisor": pd.read_excel("Target Supervisor.xlsx"),
        "target_evak": pd.read_excel("Target Evak.xlsx"),

        "mapping": pd.read_excel("Mapping.xlsx"),
        "codes": pd.read_excel("Code.xlsx")
    }


# =========================
# 🎯 TARGET PIPELINE (FIXED 🔥)
# =========================
def build_target_pipeline(df, id_name, mapping, codes):

    df = df.copy()
    mapping = mapping.copy()
    codes = codes.copy()

    df.columns = df.columns.str.strip()

    fixed_cols = [c for c in ["Year", "Product Code", "Old Product Name", "Sales Price"] if c in df.columns]
    exclude_cols = fixed_cols + ["Product Name"]
    dynamic_cols = [c for c in df.columns if c not in exclude_cols]

    df = df.melt(
        id_vars=fixed_cols,
        value_vars=dynamic_cols,
        var_name=id_name,
        value_name="Target (Unit)"
    )

    df[id_name] = pd.to_numeric(
        df[id_name].astype(str).str.replace(r"[^0-9]", "", regex=True),
        errors="coerce"
    )

    df["Product Code"] = pd.to_numeric(df["Product Code"], errors="coerce")
    mapping["Product Code"] = pd.to_numeric(mapping["Product Code"], errors="coerce")

    mapping = mapping.drop_duplicates("Product Code")
    df = df.merge(mapping, on="Product Code", how="left")

    # 🔥 مهم
    codes[id_name] = pd.to_numeric(codes[id_name], errors="coerce")
    df = df.merge(codes, on=id_name, how="left")

    df["Target (Unit)"] = pd.to_numeric(df["Target (Unit)"], errors="coerce").fillna(0)
    df["Sales Price"] = pd.to_numeric(df["Sales Price"], errors="coerce").fillna(0)

    df["Full Value"] = df["Target (Unit)"] * df["Sales Price"]

    full = df.copy()
    full["Value"] = full["Full Value"]

    def group(d, level):
        return d.groupby(level, as_index=False)["Value"].sum()

    levels = [id_name, "Manager Code", "Area Code", "Supervisor Code"]

    results = {}
    for lvl in levels:
        if lvl in df.columns:
            results[lvl] = group(full, lvl)

    return results


# =========================
# 💰 SALES PIPELINE
# =========================
def build_sales_pipeline(sales, mapping, codes):

    sales = sales.copy()
    sales.columns = sales.columns.str.strip()

    # CLEAN
    sales = sales[sales['Date'].notna()].copy()

    # NUMERIC
    for col in ['Sales Unit Before Edit','Returns Unit Before Edit','Sales Price','Invoice Discounts']:
        if col in sales.columns:
            sales[col] = pd.to_numeric(sales[col], errors='coerce').fillna(0)

    # IDS
    sales['Rep Code'] = pd.to_numeric(sales['Rep Code'], errors='coerce').astype('Int64')
    codes['Rep Code'] = pd.to_numeric(codes['Rep Code'], errors='coerce').astype('Int64')

    # MERGE
    sales = sales.merge(codes, on='Rep Code', how='left')

    # CALC
    sales['Total Sales Value'] = sales['Sales Unit Before Edit'] * sales['Sales Price']

    def group(df, cols):
        return df.groupby(cols, as_index=False)['Total Sales Value'].sum()

    return {
        "rep": group(sales, ['Rep Code']),
        "manager": group(sales, ['Manager Code']),
        "area": group(sales, ['Area Code']),
        "supervisor": group(sales, ['Supervisor Code'])
    }


# =========================
# ⏳ OVERDUE PIPELINE
# =========================
def build_overdue_pipeline(overdue, codes):

    overdue = overdue.iloc[:, :9].copy()

    overdue.columns = [
        "Client Name","Client Code","15","30","60","90","120","120+","Balance"
    ]

    for col in ["120","120+"]:
        overdue[col] = pd.to_numeric(overdue[col], errors="coerce").fillna(0)

    overdue["Overdue"] = overdue["120"] + overdue["120+"]

    overdue["Rep Code"] = pd.NA
    mask = overdue["Client Name"].astype(str).str.strip().eq("كود المندوب")
    overdue.loc[mask, "Rep Code"] = overdue.loc[mask, "Client Code"]
    overdue["Rep Code"] = overdue["Rep Code"].ffill()

    overdue = overdue[overdue["Client Code"].notna()].copy()

    overdue["Rep Code"] = pd.to_numeric(overdue["Rep Code"], errors="coerce").astype("Int64")
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce").astype("Int64")

    overdue = overdue.merge(codes, on="Rep Code", how="left")

    def group(df, col):
        return df.groupby(col, as_index=False)["Overdue"].sum()

    return {
        "rep": group(overdue, "Rep Code"),
        "manager": group(overdue, "Manager Code"),
        "area": group(overdue, "Area Code"),
        "supervisor": group(overdue, "Supervisor Code")
    }


# =========================
# 🏦 OPENING PIPELINE
# =========================
def build_opening_pipeline(opening, codes):

    opening.columns = [
        'Branch',"Evak",'Opening Balance','Sales','Returns',
        'Sales Before Discount','Cash','Checks',
        'Returned','Returned Checks',"Extra",'Daienah','End Balance'
    ]

    opening["Rep Code"] = pd.NA
    mask = opening["Branch"].astype(str).str.strip().eq("كود المندوب")
    opening.loc[mask, "Rep Code"] = opening.loc[mask, "Opening Balance"]
    opening["Rep Code"] = opening["Rep Code"].ffill()

    opening["Rep Code"] = pd.to_numeric(opening["Rep Code"], errors="coerce").astype("Int64")
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce").astype("Int64")

    opening = opening.merge(codes, on="Rep Code", how="left")

    def group(df, col):
        return df.groupby(col, as_index=False)["End Balance"].sum()

    return {
        "rep": group(opening, "Rep Code"),
        "manager": group(opening, "Manager Code"),
        "area": group(opening, "Area Code"),
        "supervisor": group(opening, "Supervisor Code")
    }
