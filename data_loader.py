import pandas as pd

def load_all():

    sales = pd.read_excel("Sales.xlsx")
    codes = pd.read_excel("Code.xlsx")

    sales.columns = sales.columns.str.strip()
    codes.columns = codes.columns.str.strip()

    # 🔥 بس نعمل merge بدون لمس أعمدة مش موجودة
    sales = sales.merge(codes, on="Rep Code", how="left")

    return {"sales": sales}
