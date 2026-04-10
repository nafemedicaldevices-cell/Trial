import pandas as pd

def load_data():

    sales = pd.read_excel("Sales.xlsx")
    overdue = pd.read_excel("Overdue.xlsx")
    extra_discounts = pd.read_excel("Extradiscounts.xlsx")
    opening = pd.read_excel("Opening.xlsx")
    opening_detail = pd.read_excel("Opening Detail.xlsx")

    target_manager = pd.read_excel("Target Manager.xlsx")
    target_area = pd.read_excel("Target Area.xlsx")
    target_rep = pd.read_excel("Target Rep.xlsx")

    mapping = pd.read_excel("Mapping.xlsx")
    codes = pd.read_excel("Code.xlsx")

    return {
        "sales": sales,
        "overdue": overdue,
        "extra_discounts": extra_discounts,
        "opening": opening,
        "opening_detail": opening_detail,
        "target_manager": target_manager,
        "target_area": target_area,
        "target_rep": target_rep,
        "mapping": mapping,
        "codes": codes
    }
