import pandas as pd
import numpy as np
import os

# =========================
# 🎯 LOAD TARGETS
# =========================
def load_targets():

    FILES = {
        "Rep": "Target Rep.xlsx",
    }

    all_data = []

    for _, file in FILES.items():

        sheets = pd.read_excel(file, sheet_name=None)

        for _, df in sheets.items():

            df.columns = df.columns.str.strip()

            fixed_cols = ["Year", "Product Code", "Old Product Name", "Sales Price"]

            df = df.melt(
                id_vars=fixed_cols,
                var_name="Code",
                value_name="Target (Year)"
            )

            df["Target (Year)"] = pd.to_numeric(df["Target (Year)"], errors="coerce")

            df["Target (Unit)"] = df["Target (Year)"] / 12
            df["Target (Value)"] = df["Target (Unit)"] * df["Sales Price"]

            months = [
                "Jan","Feb","Mar","Apr","May","Jun",
                "Jul","Aug","Sep","Oct","Nov","Dec"
            ]

            df_long = df.loc[df.index.repeat(12)].copy()
            df_long["Month"] = months * len(df)

            df_long["Target (Value)"] = df["Target (Value)"].repeat(12).values

            df_long["Code"] = df_long["Code"].astype(str).str.strip()

            all_data.append(df_long)

    return pd.concat(all_data, ignore_index=True)


# =========================
# 💰 LOAD SALES (SAFE)
# =========================
def load_sales():

    if not os.path.exists("Sales.xlsx"):
        raise Exception("❌ Sales.xlsx not found")

    df = pd.read_excel("Sales.xlsx")

    df.columns = df.columns.str.strip()

    # 🔥 auto detect rep column
    rep_candidates = ["Rep Code", "Rep", "Sales Rep Code"]

    rep_col = None
    for c in rep_candidates:
        if c in df.columns:
            rep_col = c
            break

    if rep_col is None:
        raise Exception(f"❌ No Rep column found: {df.columns.tolist()}")

    df["Rep Code"] = df[rep_col].astype(str).str.strip()

    # numeric cleanup
    for col in ["Sales Value", "Returns Value", "Invoice Discounts"]:
        if col not in df.columns:
            df[col] = 0
        else:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # net sales
    df["Net Sales"] = (
        df["Sales Value"]
        - df["Returns Value"]
        - df["Invoice Discounts"]
    )

    return df
