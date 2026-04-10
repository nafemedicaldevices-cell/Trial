import pandas as pd

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
        mapping[["Product Code", "Product Name"]],
        on="Product Code",
        how="left"
    )

    # BASE VALUE
    df["Full Target Value"] = df["Target (Unit)"] * df["Sales Price"]

    # =========================
    # TIME LOGIC
    # =========================
    current_month = pd.Timestamp.today().month
    current_quarter = (current_month - 1) // 3 + 1

    # KPI FUNCTION
    def add(df_in, factor):
        tmp = df_in.copy()
        tmp["Target (Value)"] = (tmp["Full Target Value"] / 12) * factor
        return tmp

    # KPIs
    df_full = add(df, 12)
    df_month = add(df, 1)
    df_quarter = add(df, current_quarter * 3)
    df_ytd = add(df, current_month)

    # GROUP
    def group(d):
        return d.groupby([id_name], as_index=False)["Target (Value)"].sum()

    return {
        "value_full": group(df_full),
        "value_month": group(df_month),
        "value_quarter": group(df_quarter),
        "value_uptodate": group(df_ytd),
    }
