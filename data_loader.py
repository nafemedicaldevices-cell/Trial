from cleaning import (
    load_haraka,
    load_overdue,
    load_client_haraka
)

import pandas as pd

def load_all():

    sales = pd.read_excel("Sales.xlsx")
    codes = pd.read_excel("Code.xlsx")

    sales.columns = sales.columns.str.strip()
    codes.columns = codes.columns.str.strip()

    sales["Rep Code"] = pd.to_numeric(sales["Rep Code"], errors="coerce")
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")

    sales = sales.merge(codes, on="Rep Code", how="left")

    return {
        "sales": sales,
        "haraka": load_haraka(),
        "overdue": load_overdue("Overdue.xlsx", codes),
        "client": load_client_haraka()
    }
