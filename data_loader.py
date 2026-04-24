import pandas as pd

def load_all():

    sales = pd.read_excel("Sales.xlsx")
    codes = pd.read_excel("Code.xlsx")

    sales.columns = sales.columns.str.strip()
    codes.columns = codes.columns.str.strip()

    # 🔥 تحقق من وجود العمود قبل استخدامه
    if "Rep Code" not in sales.columns:
        raise ValueError("Rep Code column missing in Sales.xlsx")

    if "Rep Code" not in codes.columns:
        raise ValueError("Rep Code column missing in Code.xlsx")

    sales["Rep Code"] = pd.to_numeric(sales["Rep Code"], errors="coerce")
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")

    sales = sales.merge(codes, on="Rep Code", how="left")

    return {
        "sales": sales
    }
