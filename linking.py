import pandas as pd

# =========================
# 📌 LOAD HELPER
# =========================

def load_file(path):
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip()
    return df


# =========================
# 🔗 BUILD MODEL
# =========================

def build_model():

    # =========================
    # 📥 LOAD DATA
    # =========================
    sales = load_file("Sales.xlsx")
    mapping = load_file("Mapping.xlsx")
    structure = load_file("Structure.xlsx")
    codes = load_file("Code.xlsx")

    # =========================
    # 🧹 CLEAN KEYS
    # =========================
    sales["Rep Code"] = pd.to_numeric(sales["Rep Code"], errors="coerce")
    mapping["Old Product Code"] = pd.to_numeric(mapping["Old Product Code"], errors="coerce")
    structure["Rep Code"] = pd.to_numeric(structure["Rep Code"], errors="coerce")
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")

    # =========================
    # 🔗 PRODUCT LINKING
    # =========================
    sales = sales.merge(
        mapping[
            [
                "Old Product Code",
                "Product Name",
                "Product Code",
                "Category",
                "Next Factor"
            ]
        ],
        on="Old Product Code",
        how="left"
    )

    # =========================
    # 🔗 STRUCTURE LINKING (FILTER DIMENSIONS)
    # =========================
    sales = sales.merge(
        structure,
        on="Rep Code",
        how="left"
    )

    # =========================
    # 🔗 CODES LINKING (OPTIONAL INFO)
    # =========================
    sales = sales.merge(
        codes,
        on="Rep Code",
        how="left"
    )

    # =========================
    # 📅 DATE FEATURES
    # =========================
    sales["Date"] = pd.to_datetime(sales["Date"], errors="coerce")

    sales["Year"] = sales["Date"].dt.year
    sales["Month"] = sales["Date"].dt.month
    sales["Month Name"] = sales["Date"].dt.strftime("%b")

    # =========================
    # 📊 KPI CALCULATIONS
    # =========================
    sales["Total Sales Value"] = (
        sales["Sales Unit Before Edit"] *
        sales["Sales Price"]
    )

    sales["Returns Value"] = (
        sales["Returns Unit Before Edit"] *
        sales["Sales Price"]
    )

    sales["Net Sales"] = (
        sales["Total Sales Value"] -
        sales["Returns Value"]
    )

    # =========================
    # 📦 LOAD OTHER MODULES
    # =========================
    from cleaning import (
        load_targets,
        load_haraka,
        load_overdue,
        load_client_haraka
    )

    targets = load_targets()
    haraka = load_haraka()
    overdue = load_overdue("Overdue.xlsx", codes)
    client_haraka = load_client_haraka()

    # =========================
    # 📤 RETURN MODEL
    # =========================
    return {
        "sales": sales,
        "targets": targets,
        "haraka": haraka,
        "overdue": overdue,
        "client_haraka": client_haraka
    }
