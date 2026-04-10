import pandas as pd
import numpy as np

# =========================
# TIME LOGIC
# =========================
current_month = pd.Timestamp.today().month
current_quarter = (current_month - 1) // 3 + 1


# =========================
# LOAD DATA
# =========================
def load_data():
    return {
        "target_rep": pd.read_excel("Target Rep.xlsx"),
        "target_manager": pd.read_excel("Target Manager.xlsx"),
        "target_area": pd.read_excel("Target Area.xlsx"),
        "target_supervisor": pd.read_excel("Target Supervisor.xlsx"),
        "target_evak": pd.read_excel("Target Evak.xlsx"),

        "mapping": pd.read_excel("Mapping.xlsx"),
    }


# =========================
# TARGET PIPELINE
# =========================
def build_target_pipeline(df, id_name, mapping):

    df = df.copy()
    mapping = mapping.copy()

    # CLEAN COLUMNS
    df.columns = df.columns.str.strip()

    fixed_cols = [c for c in ["Year", "Product Code", "Old Product Name", "Sales Price"] if c in df.columns]
    dynamic_cols = [c for c in df.columns if c not in fixed_cols]

    # MELT
    df = df.melt(
        id_vars=fixed_cols,
        value_vars=dynamic_cols,
        var_name=id_name,
        value_name="Target (Unit)"
    )

    # CLEAN IDS
    df[id_name] = pd.to_numeric(
        df[id_name].astype(str).str.replace(r"[^0-9]", "", regex=True),
        errors="coerce"
    )

    # NUMERIC
    df["Product Code"] = pd.to_numeric(df["Product Code"], errors="coerce")
    df["Target (Unit)"] = pd.to_numeric(df["Target (Unit)"], errors="coerce").fillna(0)
    df["Sales Price"] = pd.to_numeric(df["Sales Price"], errors="coerce").fillna(0)

    # MAPPING
    mapping["Product Code"] = pd.to_numeric(mapping["Product Code"], errors="coerce")
    mapping = mapping.drop_duplicates("Product Code")

    df = df.merge(
        mapping[["Product Code", "Product Name", "Category", "2 Classification"]],
        on="Product Code",
        how="left"
    )

    # BASE VALUE
    df["Full Target Value"] = df["Target (Unit)"] * df["Sales Price"]

    # =========================
    # KPI CALCULATION
    # =========================
    def add(df_in, factor):
        tmp = df_in.copy()
        tmp["Target (Value)"] = (tmp["Full Target Value"] / 12) * factor
        return tmp

    df_full = add(df, 12)
    df_month = add(df, 1)

    # ✅ Quarter ديناميك
    df_quarter = add(df, current_quarter * 3)

    # ✅ YTD ديناميك
    df_ytd = add(df, current_month)

    # =========================
    # GROUP VALUE
    # =========================
    def value(d):
        return d.groupby([id_name], as_index=False)["Target (Value)"].sum()

    # =========================
    # GROUP PRODUCTS
    # =========================
    def products(d):
        return d.groupby(
            [id_name, "Product Code", "Product Name"],
            as_index=False
        )["Target (Value)"].sum()

    return {
        # RAW
        "full": df,

        # VALUES
        "value_full": value(df_full),
        "value_month": value(df_month),
        "value_quarter": value(df_quarter),
        "value_uptodate": value(df_ytd),

        # PRODUCTS
        "products_full": products(df_full),
        "products_month": products(df_month),
        "products_quarter": products(df_quarter),
        "products_uptodate": products(df_ytd),
    }
