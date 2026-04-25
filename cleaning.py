import pandas as pd
import numpy as np

# =========================
# LOAD TARGETS
# =========================
def load_targets():
    file = "Target Rep.xlsx"

    df = pd.read_excel(file, sheet_name=None)

    all_data = []

    for sheet, data in df.items():

        data.columns = data.columns.str.strip()

        fixed_cols = ["Year", "Product Code", "Old Product Name", "Sales Price"]

        data = data.melt(
            id_vars=fixed_cols,
            var_name="Rep Code",
            value_name="Target (Year)"
        )

        data["Target (Year)"] = pd.to_numeric(data["Target (Year)"], errors="coerce")

        data["Target (Unit)"] = data["Target (Year)"] / 12
        data["Target (Value)"] = data["Target (Unit)"] * data["Sales Price"]

        data["Rep Code"] = data["Rep Code"].astype(str).str.strip()

        all_data.append(data)

    return pd.concat(all_data, ignore_index=True)


# =========================
# LOAD HARKA
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
# BUILD FINAL TABLE
# =========================
def build_sales_vs_target(targets, sales):

    sales_agg = sales.groupby("Rep Code", as_index=False)["Sales Value"].sum()

    df = targets.merge(sales_agg, on="Rep Code", how="left")

    df["Sales Value"] = df["Sales Value"].fillna(0)

    df["Target Unit"] = df["Target (Unit)"].fillna(0)
    df["Target Value"] = df["Target (Value)"].fillna(0)

    df["Sales Unit"] = df["Sales Value"]

    df["Achievement %"] = np.where(
        df["Target Value"] > 0,
        (df["Sales Value"] / df["Target Value"]) * 100,
        0
    )

    return df
