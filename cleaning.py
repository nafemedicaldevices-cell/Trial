import pandas as pd
import numpy as np


# =========================
# LOAD TARGETS
# =========================
def load_targets():

    file = "Target Rep.xlsx"
    sheets = pd.read_excel(file, sheet_name=None)

    all_data = []

    for _, df in sheets.items():

        df.columns = df.columns.str.strip()

        fixed_cols = ["Year", "Product Code", "Old Product Name", "Sales Price"]

        df = df.melt(
            id_vars=fixed_cols,
            var_name="Rep Code",
            value_name="Target (Year)"
        )

        df["Target (Year)"] = pd.to_numeric(df["Target (Year)"], errors="coerce")

        df["Target (Unit)"] = df["Target (Year)"] / 12
        df["Target (Value)"] = df["Target (Unit)"] * df["Sales Price"]

        df["Rep Code"] = df["Rep Code"].astype(str).str.strip()

        all_data.append(df)

    return pd.concat(all_data, ignore_index=True)


# =========================
# LOAD SALES
# =========================
def load_haraka():

    df = pd.read_excel("Rep Harakah.xlsx")
    df.columns = df.columns.str.strip()

    df = df.rename(columns={
        df.columns[0]: "Rep Code",
        df.columns[3]: "Sales Value"
    })

    df["Rep Code"] = df["Rep Code"].astype(str).str.strip()
    df["Sales Value"] = pd.to_numeric(df["Sales Value"], errors="coerce").fillna(0)

    return df


# =========================
# LOAD CODE FILE
# =========================
def load_codes():

    df = pd.read_excel("Code.xlsx")
    df.columns = df.columns.str.strip()

    df["Rep Code"] = df["Rep Code"].astype(str).str.strip()

    return df


# =========================
# MERGE EVERYTHING
# =========================
def build_sales_vs_target(targets, sales, codes):

    import numpy as np

    # sales aggregation
    sales_agg = sales.groupby("Rep Code", as_index=False)["Sales Value"].sum()

    # merge target + sales
    df = targets.merge(sales_agg, on="Rep Code", how="left")

    # merge with codes (IMPORTANT)
    df = df.merge(codes, on="Rep Code", how="left")

    df["Sales Value"] = df["Sales Value"].fillna(0)

    df["Achievement %"] = np.where(
        df["Target (Value)"] > 0,
        (df["Sales Value"] / df["Target (Value)"]) * 100,
        0
    )

    return df
