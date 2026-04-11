import pandas as pd
import numpy as np

# =========================
# LOAD DATA
# =========================
def load_data():
    return {
        "sales": pd.read_excel("Sales.xlsx"),
        "overdue": pd.read_excel("Overdue.xlsx"),
        "opening": pd.read_excel("Opening.xlsx"),
        "mapping": pd.read_excel("Mapping.xlsx"),
        "codes": pd.read_excel("Code.xlsx")
    }


# =========================
# SALES PIPELINE
# =========================
def build_sales_pipeline(sales, mapping, codes):

    sales = sales.copy()
    sales.columns = sales.columns.str.strip()

    # NUMERIC
    for col in ['Sales Value','Invoice Discounts']:
        if col in sales.columns:
            sales[col] = pd.to_numeric(sales[col], errors='coerce').fillna(0)

    # MERGE CODES
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")
    sales["Rep Code"] = pd.to_numeric(sales["Rep Code"], errors="coerce")

    sales = sales.merge(codes, on="Rep Code", how="left")

    # KPI
    sales["Net Sales"] = sales["Sales Value"] - sales["Invoice Discounts"]

    # GROUP
    rep = sales.groupby("Rep Code")[["Sales Value","Invoice Discounts","Net Sales"]].sum().reset_index()
    manager = sales.groupby("Manager Code")[["Sales Value","Invoice Discounts","Net Sales"]].sum().reset_index()

    return rep, manager


# =========================
# OVERDUE PIPELINE
# =========================
def build_overdue_pipeline(overdue, codes):

    overdue.columns = overdue.columns[:9]

    overdue.columns = [
        "Client Name","Client Code","15","30","60","90","120","120+","Balance"
    ]

    for col in ["120","120+"]:
        overdue[col] = pd.to_numeric(overdue[col], errors="coerce").fillna(0)

    overdue["Overdue"] = overdue["120"] + overdue["120+"]

    overdue["Rep Code"] = overdue["Client Code"]
    overdue["Rep Code"] = pd.to_numeric(overdue["Rep Code"], errors="coerce")

    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")

    overdue = overdue.merge(codes, on="Rep Code", how="left")

    rep = overdue.groupby("Rep Code")["Overdue"].sum().reset_index()
    manager = overdue.groupby("Manager Code")["Overdue"].sum().reset_index()

    return rep, manager


# =========================
# OPENING PIPELINE
# =========================
def build_opening_pipeline(opening, codes):

    opening.columns = opening.columns[:13]

    opening.columns = [
        'Branch',"Evak",'Opening','Sales','Returns','Before Discount',
        'Cash','Checks','Returned','Returned Checks',
        "Extra",'Daienah','End'
    ]

    for col in ['Opening','Cash','Checks','Extra','End']:
        opening[col] = pd.to_numeric(opening[col], errors='coerce').fillna(0)

    opening["Rep Code"] = pd.to_numeric(opening["Opening"], errors="coerce")

    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")

    opening = opening.merge(codes, on="Rep Code", how="left")

    rep = opening.groupby("Rep Code")[["Opening","Cash","Checks","Extra","End"]].sum().reset_index()
    manager = opening.groupby("Manager Code")[["Opening","Cash","Checks","Extra","End"]].sum().reset_index()

    return rep, manager
