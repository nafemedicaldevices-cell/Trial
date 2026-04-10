import pandas as pd
import numpy as np


# =========================
# LOAD DATA
# =========================
def load_data():

    sales = pd.read_excel("Sales.xlsx")
    overdue = pd.read_excel("Overdue.xlsx")
    opening_detail = pd.read_excel("Opening Detail.xlsx")
    mapping = pd.read_excel("Mapping.xlsx")
    codes = pd.read_excel("Code.xlsx")

    return sales, overdue, opening_detail, mapping, codes


# =========================
# CLEAN SALES (100% SAFE)
# =========================
def clean_sales(sales, mapping, codes):

    sales.columns = sales.columns.str.strip()

    # -------------------------
    # CREATE ALL POSSIBLE COLUMNS SAFELY
    # -------------------------
    needed_cols = [
        "Rep Code",
        "Old Product Code",
        "Old Product Name",
        "Manager Code",
        "Area Code",
        "Sales Unit Before Edit",
        "Returns Unit Before Edit",
        "Sales Price"
    ]

    for col in needed_cols:
        if col not in sales.columns:
            sales[col] = np.nan

    # -------------------------
    # PRODUCT HEADER EXTRACTION
    # -------------------------
    if "Date" in sales.columns:

        mask = sales["Date"].astype(str).str.strip().eq("كود الصنف")

        if "Warehouse Name" in sales.columns:
            sales.loc[mask, "Old Product Code"] = sales.loc[mask, "Warehouse Name"]

        if "Client Code" in sales.columns:
            sales.loc[mask, "Old Product Name"] = sales.loc[mask, "Client Code"]

        sales[["Old Product Code","Old Product Name"]] = sales[
            ["Old Product Code","Old Product Name"]
        ].ffill()

    # -------------------------
    # NUMERIC CONVERSION SAFE
    # -------------------------
    for col in ["Rep Code", "Old Product Code", "Manager Code", "Area Code"]:
        if col in sales.columns:
            sales[col] = pd.to_numeric(sales[col], errors="coerce")

    # -------------------------
    # MERGE SAFE
    # -------------------------
    if mapping is not None and "Old Product Code" in sales.columns:
        sales = sales.merge(mapping, on="Old Product Code", how="left")

    if codes is not None and "Rep Code" in sales.columns:
        sales = sales.merge(codes, on="Rep Code", how="left")

    # -------------------------
    # KPI CALCULATION SAFE
    # -------------------------
    sales["Total Sales Value"] = (
        sales["Sales Unit Before Edit"].fillna(0) *
        sales["Sales Price"].fillna(0)
    )

    sales["Returns Value"] = (
        sales["Returns Unit Before Edit"].fillna(0) *
        sales["Sales Price"].fillna(0)
    )

    sales["Sales After Returns"] = sales["Total Sales Value"] - sales["Returns Value"]

    sales["Net Sales Unit"] = (
        sales["Sales Unit Before Edit"].fillna(0) -
        sales["Returns Unit Before Edit"].fillna(0)
    )

    return sales


# =========================
# CLEAN OVERDUE
# =========================
def clean_overdue(overdue):

    overdue = overdue.iloc[:, :9].copy()

    overdue.columns = [
        "Client Name","Client Code","15 Days","30 Days","60 Days",
        "90 Days","120 Days","More Than 120 Days","Balance"
    ]

    overdue["Overdue"] = (
        overdue["120 Days"].fillna(0) +
        overdue["More Than 120 Days"].fillna(0)
    )

    return overdue


# =========================
# CLEAN OPENING DETAIL
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

    mask = opening_detail["Client Code"].astype(str).str.strip().eq("كود الفرع")

    opening_detail.loc[mask, "Rep Code"] = opening_detail.loc[mask, "Returns"]

    opening_detail["Rep Code"] = pd.to_numeric(opening_detail["Rep Code"], errors="coerce")

    opening_detail = opening_detail.merge(codes, on="Rep Code", how="left")

    return opening_detail


# =========================
# MAIN PIPELINE
# =========================
def run_pipeline():

    sales, overdue, opening_detail, mapping, codes = load_data()

    sales = clean_sales(sales, mapping, codes)
    overdue = clean_overdue(overdue)
    opening_detail = clean_opening_detail(opening_detail, codes)

    return {
        "sales": sales,
        "overdue": overdue,
        "opening_detail": opening_detail
    }
