import pandas as pd
import numpy as np

# =========================
# 📅 TIME
# =========================
current_month = pd.Timestamp.today().month
current_quarter = (current_month - 1) // 3 + 1
past_quarters = max(current_quarter - 1, 1)


# =========================
# 📂 LOAD DATA
# =========================
def load_data():
    return {
        "sales": pd.read_excel("Sales.xlsx"),
        "overdue": pd.read_excel("Overdue.xlsx"),
        "extra_discounts": pd.read_excel("Extradiscounts.xlsx"),
        "opening": pd.read_excel("Opening.xlsx"),
        "opening_detail": pd.read_excel("Opening Detail.xlsx"),

        "target_manager": pd.read_excel("Target Manager.xlsx"),
        "target_area": pd.read_excel("Target Area.xlsx"),
        "target_rep": pd.read_excel("Target Rep.xlsx"),
        "target_supervisor": pd.read_excel("Target Supervisor.xlsx"),
        "target_evak": pd.read_excel("Target Evak.xlsx"),

        "mapping": pd.read_excel("Mapping.xlsx"),
        "codes": pd.read_excel("Code.xlsx")
    }


# =========================
# 🚀 TARGET PIPELINE (NO MERGE WITH SALES)
# =========================
def build_target_pipeline(df, id_name, mapping):

    df = df.copy()
    mapping = mapping.copy()

    df.columns = df.columns.str.strip()
    mapping.columns = mapping.columns.str.strip()

    fixed_cols = [c for c in ["Year", "Product Code", "Old Product Name", "Sales Price"] if c in df.columns]
    dynamic_cols = [c for c in df.columns if c not in fixed_cols]

    # reshape
    df = df.melt(
        id_vars=fixed_cols,
        value_vars=dynamic_cols,
        var_name=id_name,
        value_name="Target (Unit)"
    )

    # clean IDs
    df[id_name] = pd.to_numeric(
        df[id_name].astype(str).str.replace(r"[^0-9]", "", regex=True),
        errors="coerce"
    )

    df["Product Code"] = pd.to_numeric(df["Product Code"], errors="coerce")
    mapping["Product Code"] = pd.to_numeric(mapping["Product Code"], errors="coerce")

    mapping = mapping.drop_duplicates("Product Code")

    # merge mapping (TARGET ONLY)
    df = df.merge(mapping, on="Product Code", how="left")

    # numeric clean
    df["Target (Unit)"] = pd.to_numeric(df["Target (Unit)"], errors="coerce").fillna(0)
    df["Sales Price"] = pd.to_numeric(df["Sales Price"], errors="coerce").fillna(0)

    # value
    df["Full Value"] = df["Target (Unit)"] * df["Sales Price"]

    # =========================
    # KPI LOGIC
    # =========================
    full = df.copy()

    month = df.copy()
    month["Value"] = full["Full Value"] * (current_month / 12)

    ytd = df.copy()
    ytd["Value"] = full["Full Value"] * (current_month / 12)

    quarter = df.copy()
    quarter["Value"] = full["Full Value"] * (past_quarters / 4)

    full["Value"] = full["Full Value"]

    # =========================
    # VALUE TABLE
    # =========================
    def group(d):
        return d.groupby([id_name], as_index=False)["Value"].sum()

    value_table = group(full).rename(columns={"Value": "Full Year 🏆"})
    value_table["Month 📅"] = group(month)["Value"]
    value_table["Quarter 📊"] = group(quarter)["Value"]
    value_table["YTD 📈"] = group(ytd)["Value"]

    # =========================
    # PRODUCTS TABLE
    # =========================
    def product_group(d):
        return d.groupby(
            [id_name, "Product Code", "Product Name"],
            as_index=False
        ).agg(
            Units=("Target (Unit)", "sum"),
            Value=("Value", "sum")
        )

    return {
        "value_table": value_table,
        "products_full": product_group(full),
        "products_month": product_group(month),
        "products_quarter": product_group(quarter),
        "products_ytd": product_group(ytd),
    }
