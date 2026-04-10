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

    return {
        "target": target
    }
