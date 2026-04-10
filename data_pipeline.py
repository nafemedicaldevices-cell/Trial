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
