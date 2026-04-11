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

        "target_manager": pd.read_excel("Target Manager.xlsx"),
        "target_area": pd.read_excel("Target Area.xlsx"),
        "target_rep": pd.read_excel("Target Rep.xlsx"),
        "target_supervisor": pd.read_excel("Target Supervisor.xlsx"),
        "target_evak": pd.read_excel("Target Evak.xlsx"),

        "mapping": pd.read_excel("Mapping.xlsx"),
        "codes": pd.read_excel("Code.xlsx")
    }


# =========================
# 🧠 SAFE GROUP HELPER
# =========================
def safe_group(df, group_cols, sum_cols):
    group_cols = [c for c in group_cols if c in df.columns]
    sum_cols = [c for c in sum_cols if c in df.columns]

    if not group_cols:
        return pd.DataFrame()

    return df.groupby(group_cols, as_index=False)[sum_cols].sum()


# =========================
# 🎯 TARGET PIPELINE
# =========================
def build_target_pipeline(df, id_name, mapping):

    df = df.copy()
    df.columns = df.columns.str.strip()

    fixed_cols = [c for c in ["Year", "Product Code", "Product Name", "Sales Price"] if c in df.columns]
    dynamic_cols = [c for c in df.columns if c not in fixed_cols]

    df = df.melt(
        id_vars=fixed_cols,
        value_vars=dynamic_cols,
        var_name=id_name,
        value_name="Target (Unit)"
    )

    df[id_name] = pd.to_numeric(df[id_name].astype(str).str.replace(r"[^0-9]", "", regex=True), errors="coerce")

    df["Product Code"] = pd.to_numeric(df["Product Code"], errors="coerce")
    mapping["Product Code"] = pd.to_numeric(mapping["Product Code"], errors="coerce")

    df = df.merge(mapping, on="Product Code", how="left")

    df["Target (Unit)"] = pd.to_numeric(df["Target (Unit)"], errors="coerce").fillna(0)
    df["Sales Price"] = pd.to_numeric(df["Sales Price"], errors="coerce").fillna(0)

    df["Value"] = df["Target (Unit)"] * df["Sales Price"]

    return {
        "value": safe_group(df, [id_name], ["Value"]),
        "products": safe_group(df, [id_name, "Product Code", "Product Name"], ["Value", "Target (Unit)"])
    }


# =========================
# 💰 SALES PIPELINE
# =========================
def build_sales_pipeline(sales, mapping, codes):

    sales = sales.copy()
    sales.columns = sales.columns.str.strip()

    sales = sales.dropna(how="all")

    num_cols = [
        "Sales Unit Before Edit",
        "Returns Unit Before Edit",
        "Sales Price",
        "Invoice Discounts"
    ]

    for c in num_cols:
        if c in sales.columns:
            sales[c] = pd.to_numeric(sales[c], errors="coerce").fillna(0)

    sales["Total Sales Value"] = sales["Sales Unit Before Edit"] * sales["Sales Price"]
    sales["Returns Value"] = sales["Returns Unit Before Edit"] * sales["Sales Price"]
    sales["Net Sales"] = sales["Total Sales Value"] - sales["Returns Value"]

    sales = sales.merge(codes, on="Rep Code", how="left")

    return {
        "rep": safe_group(sales, ["Rep Code"], ["Net Sales", "Invoice Discounts"]),
        "manager": safe_group(sales, ["Manager Code"], ["Net Sales"]),
        "area": safe_group(sales, ["Area Code"], ["Net Sales"]),
        "supervisor": safe_group(sales, ["Supervisor Code"], ["Net Sales"])
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

    df = df.merge(codes, on="Rep Code", how="left")

    return {
        "rep": safe_group(df, ["Rep Code"], ["Opening","TotalCollection","EndBalance"]),
        "manager": safe_group(df, ["Manager Code"], ["Opening","EndBalance"]),
        "area": safe_group(df, ["Area Code"], ["Opening","EndBalance"]),
        "supervisor": safe_group(df, ["Supervisor Code"], ["Opening","EndBalance"])
    }
