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
# CLEAN SALES (SAFE)
# =========================
def clean_sales(sales, mapping, codes):

    sales.columns = sales.columns.str.strip()

    # SAFE CREATE COLUMNS
    sales["Old Product Code"] = np.nan
    sales["Old Product Name"] = np.nan

    if "Date" in sales.columns:

        mask = sales["Date"].astype(str).str.strip().eq("كود الصنف")

        if "Warehouse Name" in sales.columns:
            sales.loc[mask, "Old Product Code"] = sales.loc[mask, "Warehouse Name"]

        if "Client Code" in sales.columns:
            sales.loc[mask, "Old Product Name"] = sales.loc[mask, "Client Code"]

        sales[["Old Product Code","Old Product Name"]] = sales[
            ["Old Product Code","Old Product Name"]
        ].ffill()

    sales["Old Product Code"] = pd.to_numeric(sales["Old Product Code"], errors="coerce")
    sales["Rep Code"] = pd.to_numeric(sales["Rep Code"], errors="coerce")

    # MERGE SAFE
    sales = sales.merge(mapping, on="Old Product Code", how="left")
    sales = sales.merge(codes, on="Rep Code", how="left")

    # KPI SAFE
    if "Sales Unit Before Edit" in sales.columns and "Sales Price" in sales.columns:
        sales["Total Sales Value"] = sales["Sales Unit Before Edit"] * sales["Sales Price"]
    else:
        sales["Total Sales Value"] = 0

    if "Returns Unit Before Edit" in sales.columns:
        sales["Returns Value"] = sales["Returns Unit Before Edit"] * sales["Sales Price"]
    else:
        sales["Returns Value"] = 0

    sales["Sales After Returns"] = sales["Total Sales Value"] - sales["Returns Value"]

    return sales


# =========================
# CLEAN OVERDUE
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
