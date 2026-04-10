import pandas as pd

def load_data():
    sales = pd.read_excel("Sales.xlsx")
    mapping = pd.read_excel("Mapping.xlsx")
    codes = pd.read_excel("Code.xlsx")

    return {
        "sales": sales,
        "mapping": mapping,
        "codes": codes
    }

def rep_target(data):

    df = pd.read_excel("Target Rep.xlsx")
    mapping = data["mapping"]

    df.columns = df.columns.str.strip().str.replace(r'\s+', ' ', regex=True)

    fixed_cols = ["Year", "Product Code", "Old Product Name", "Sales Price"]
    dynamic_cols = [c for c in df.columns if c not in fixed_cols]

    df = df.melt(
        id_vars=fixed_cols,
        value_vars=dynamic_cols,
        var_name="Rep Code",
        value_name="Target Unit"
    )

    df["Rep Code"] = pd.to_numeric(df["Rep Code"], errors="coerce")

    df["Product Code"] = pd.to_numeric(df["Product Code"], errors="coerce")

    df = df.merge(mapping, on="Product Code", how="left")

    df["Target Value"] = df["Target Unit"] * df["Sales Price"]

    return df.groupby("Rep Code", as_index=False)["Target Value"].sum()



def run_pipeline():

    data = load_data()

    target = rep_target(data)

    def run_pipeline():

    data = load_data()

    target = rep_target(data)

    sales = data["sales"]

    # نجمع Sales على Rep Code
    sales["Sales Value"] = pd.to_numeric(sales.get("Sales Value", 0), errors="coerce").fillna(0)

    sales_grouped = sales.groupby("Rep Code", as_index=False)["Sales Value"].sum()

    # دمج Target + Sales
    final = target.merge(sales_grouped, on="Rep Code", how="left")

    final["Sales Value"] = final["Sales Value"].fillna(0)

    final["Achievement %"] = (final["Sales Value"] / final["Target Value"]) * 100

    return {
        "kpi": final
    }

    return {
        "target": target
    }
