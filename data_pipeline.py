import pandas as pd
import numpy as np

current_month = pd.Timestamp.today().month
current_quarter = (current_month - 1) // 3 + 1
quarter_months = current_quarter * 3


# =========================
# LOAD DATA 📂
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
# TARGET PIPELINE 🚀
# =========================
def build_target_pipeline(df, id_name, mapping):

    df = df.copy()
    mapping = mapping.copy()

    df.columns = df.columns.str.strip()

    # -------------------------
    # Melt
    # -------------------------
    fixed_cols = [c for c in ["Year", "Product Code", "Old Product Name", "Sales Price"] if c in df.columns]
    dynamic_cols = [c for c in df.columns if c not in fixed_cols]

    df = df.melt(
        id_vars=fixed_cols,
        value_vars=dynamic_cols,
        var_name=id_name,
        value_name="Target (Unit)"
    )

    # -------------------------
    # Clean IDs
    # -------------------------
    df[id_name] = pd.to_numeric(
        df[id_name].astype(str).str.replace(r"[^0-9]", "", regex=True),
        errors="coerce"
    )

    df["Product Code"] = pd.to_numeric(df["Product Code"], errors="coerce")
    mapping["Product Code"] = pd.to_numeric(mapping["Product Code"], errors="coerce")

    mapping = mapping.drop_duplicates("Product Code")

    df = df.merge(mapping, on="Product Code", how="left")

    # -------------------------
    # Numeric
    # -------------------------
    df["Target (Unit)"] = pd.to_numeric(df["Target (Unit)"], errors="coerce").fillna(0)
    df["Sales Price"] = pd.to_numeric(df["Sales Price"], errors="coerce").fillna(0)

    df["Full Target Value"] = df["Target (Unit)"] * df["Sales Price"]

    # -------------------------
    # KPI builder 🔥
    # -------------------------
    def add(df_in, factor):
        tmp = df_in.copy()
        tmp["Target (Value)"] = (tmp["Full Target Value"] / 12) * factor
        return tmp

    df_full = add(df, 12)
    df_month = add(df, 1)
    df_quarter = add(df, quarter_months)
    df_ytd = add(df, current_month)

    # -------------------------
    # GROUP VALUE
    # -------------------------
    def group(d):
        return d.groupby([id_name], as_index=False)["Target (Value)"].sum()

    # -------------------------
    # PRODUCTS GROUP 📦
    # -------------------------
    def group_products(d):
        return d.groupby(
            [id_name, "Product Code", "Product Name", "Category", "2 Classification"],
            as_index=False
        )["Target (Value)"].sum()

    # =========================
    # FINAL OUTPUT 🔥
    # =========================
    return {

        # RAW
        "raw": df,

        # VALUE KPI
        "value_full": group(df_full),
        "value_month": group(df_month),
        "value_quarter": group(df_quarter),
        "value_uptodate": group(df_ytd),

        # PRODUCTS KPI 📦🔥 (FULL / MONTH / QUARTER / YTD)
        "products_full": group_products(df_full),
        "products_month": group_products(df_month),
        "products_quarter": group_products(df_quarter),
        "products_uptodate": group_products(df_ytd),
    }
