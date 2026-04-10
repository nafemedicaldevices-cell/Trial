import pandas as pd


# =========================
# 📂 LOAD DATA
# =========================
def load_data():
    return {
        # ================= SALES =================
        "sales": pd.read_excel("Sales.xlsx"),

        # ================= OVERDUE =================
        "overdue": pd.read_excel("Overdue.xlsx"),

        # ================= FINANCIAL =================
        "extra_discounts": pd.read_excel("Extradiscounts.xlsx"),
        "opening": pd.read_excel("Opening.xlsx"),
        "opening_detail": pd.read_excel("Opening Detail.xlsx"),

        # ================= TARGETS =================
        "target_manager": pd.read_excel("Target Manager.xlsx"),
        "target_area": pd.read_excel("Target Area.xlsx"),
        "target_rep": pd.read_excel("Target Rep.xlsx"),
        "target_supervisor": pd.read_excel("Target Supervisor.xlsx"),
        "target_evak": pd.read_excel("Target Evak.xlsx"),

        # ================= MASTER DATA =================
        "mapping": pd.read_excel("Mapping.xlsx"),
        "codes": pd.read_excel("Code.xlsx"),
    }
