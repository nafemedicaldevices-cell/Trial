import pandas as pd
import numpy as np

# =========================
# 📅 TIME SETTINGS
# =========================
current_month = pd.Timestamp.today().month
current_quarter = (current_month - 1) // 3 + 1
past_quarters = max(current_quarter - 1, 0)


# =========================
# 📥 LOAD ALL FILES
# =========================
def load_data():

    return {
        "sales": pd.read_excel("Sales.xlsx"),
        "overdue": pd.read_excel("Overdue.xlsx"),
        "opening": pd.read_excel("Opening.xlsx"),

        "target_rep": pd.read_excel("Target Rep.xlsx"),
        "target_manager": pd.read_excel("Target Manager.xlsx"),
        "target_area": pd.read_excel("Target Area.xlsx"),
        "target_supervisor": pd.read_excel("Target Supervisor.xlsx"),
        "target_evak": pd.read_excel("Target Evak.xlsx"),

        "mapping": pd.read_excel("Mapping.xlsx"),
        "codes": pd.read_excel("Code.xlsx"),
    }


# =========================
# 🧩 SAFE GROUP FUNCTION
# =========================
def safe_group(df, group_cols, sum_cols):
    group_cols = [c for c in group_cols if c in df.columns]
    sum_cols = [c for c in sum_cols if c in df.columns]

    if not group_cols:
        return pd.DataFrame()

    return df.groupby(group_cols, as_index=False)[sum_cols].sum()


# =========================
# 🎯 TARGET PIPELINE (FIXED)
# =========================
def build_target_pipeline(df, id_name, mapping):

    df = df.copy()
    mapping = mapping.copy()

    df.columns = df.columns.str.strip()

    fixed_cols = [c for c in ["Year", "Product Code", "Product Name", "Sales Price"] if c in df.columns]
    dynamic_cols = [c for c in df.columns if c not in fixed_cols]

    df = df.melt(
        id_vars=fixed_cols,
        value_vars=dynamic_cols,
        var_name=id_name,
        value_name="Target (Unit)"
    )

    df[id_name] = (
        df[id_name]
        .astype(str)
        .str.replace(r"[^0-9]", "", regex=True)
    )

    df[id_name] = pd.to_numeric(df[id_name], errors="coerce")
    df["Product Code"] = pd.to_numeric(df["Product Code"], errors="coerce")
    mapping["Product Code"] = pd.to_numeric(mapping["Product Code"], errors="coerce")

    mapping = mapping.drop_duplicates("Product Code")

    df = df.merge(mapping, on="Product Code", how="left")

    df["Target (Unit)"] = pd.to_numeric(df["Target (Unit)"], errors="coerce").fillna(0)

    if "Sales Price" in df.columns:
        df["Sales Price"] = pd.to_numeric(df["Sales Price"], errors="coerce").fillna(0)
    else:
        df["Sales Price"] = 0

    df["Target Value"] = df["Target (Unit)"] * df["Sales Price"]

    return {
        "value": safe_group(df, [id_name], ["Target Value"]),
        "products": safe_group(df, [id_name, "Product Code", "Product Name"], ["Target Value", "Target (Unit)"])
    }


# =========================
# 💰 SALES PIPELINE (SAFE)
# =========================
def build_sales_pipeline(df, codes):

    df = df.copy()
    df.columns = df.columns.str.strip()
    df = df.dropna(how="all")

    num_cols = [
        "Sales Unit Before Edit",
        "Returns Unit Before Edit",
        "Sales Price",
        "Invoice Discounts"
    ]

    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    if "Sales Unit Before Edit" in df.columns and "Sales Price" in df.columns:
        df["Sales Value"] = df["Sales Unit Before Edit"] * df["Sales Price"]
    else:
        df["Sales Value"] = 0

    df["Returns Value"] = df.get("Returns Unit Before Edit", 0) * df.get("Sales Price", 0)
    df["Net Sales"] = df["Sales Value"] - df["Returns Value"]

    if "Rep Code" in df.columns:
        df = df.merge(codes, on="Rep Code", how="left")

    return {
        "rep": safe_group(df, ["Rep Code"], ["Net Sales"]),
        "manager": safe_group(df, ["Manager Code"], ["Net Sales"]),
        "area": safe_group(df, ["Area Code"], ["Net Sales"]),
        "supervisor": safe_group(df, ["Supervisor Code"], ["Net Sales"])
    }


# =========================
# ⚠️ OVERDUE PIPELINE
# =========================
def build_overdue(df, codes):

    df = df.copy()
    df = df.iloc[:, :9]

    df.columns = [
        "Client Name","Client Code","15","30","60","90","120","120+","Balance"
    ]

    for c in df.columns[2:]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    df["Overdue"] = df["120"] + df["120+"]

    df["Rep Code"] = np.nan
    mask = df["Client Name"].astype(str).eq("كود المندوب")
    df.loc[mask, "Rep Code"] = df.loc[mask, "Client Code"]
    df["Rep Code"] = df["Rep Code"].ffill()

    df = df.merge(codes, on="Rep Code", how="left")

    return {
        "rep": safe_group(df, ["Rep Code"], ["Overdue"]),
        "manager": safe_group(df, ["Manager Code"], ["Overdue"]),
        "area": safe_group(df, ["Area Code"], ["Overdue"]),
        "supervisor": safe_group(df, ["Supervisor Code"], ["Overdue"])
    }


# =========================
# 🏦 OPENING PIPELINE
# =========================
def build_opening(df, codes):

    df = df.copy()

    df.columns = [
        "Branch","Evak","Opening","Sales","Returns",
        "SalesBefore","Cash","Checks","Returned","Returned2",
        "Discounts","Debt","EndBalance"
    ]

    for c in df.columns[2:]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    df["TotalCollection"] = df["Cash"] + df["Checks"]

    if "Rep Code" in df.columns:
        df = df.merge(codes, on="Rep Code", how="left")

    return {
        "rep": safe_group(df, ["Rep Code"], ["Opening","TotalCollection","EndBalance"]),
        "manager": safe_group(df, ["Manager Code"], ["Opening","EndBalance"]),
        "area": safe_group(df, ["Area Code"], ["Opening","EndBalance"]),
        "supervisor": safe_group(df, ["Supervisor Code"], ["Opening","EndBalance"])
    }


# =========================
# 🚀 MAIN RUNNER
# =========================
def run_all():

    data = load_data()

    results = {}

    # Targets
    results["target_rep"] = build_target_pipeline(data["target_rep"], "Rep Code", data["mapping"])
    results["target_manager"] = build_target_pipeline(data["target_manager"], "Manager Code", data["mapping"])
    results["target_area"] = build_target_pipeline(data["target_area"], "Area Code", data["mapping"])
    results["target_supervisor"] = build_target_pipeline(data["target_supervisor"], "Supervisor Code", data["mapping"])
    results["target_evak"] = build_target_pipeline(data["target_evak"], "Evak Code", data["mapping"])

    # Sales / Overdue / Opening
    results["sales"] = build_sales_pipeline(data["sales"], data["codes"])
    results["overdue"] = build_overdue(data["overdue"], data["codes"])
    results["opening"] = build_opening(data["opening"], data["codes"])

    return results
