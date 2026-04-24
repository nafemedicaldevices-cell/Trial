import pandas as pd
import numpy as np
import os

# =====================================================
# 🎯 TARGETS
# =====================================================
def load_targets():

    files = {
        "Rep": "Target Rep.xlsx",
        "Manager": "Target Manager.xlsx",
        "Area": "Target Area.xlsx",
        "Supervisor": "Target Supervisor.xlsx",
        "Evak": "Target Evak.xlsx",
    }

    all_data = []

    for level, file in files.items():

        df = pd.read_excel(file)
        df.columns = df.columns.str.strip()

        df = df.melt(
            id_vars=["Year", "Product Code", "Old Product Name", "Sales Price"],
            var_name="Code",
            value_name="Target (Year)"
        )

        df["Level"] = level
        df["Target (Year)"] = pd.to_numeric(df["Target (Year)"], errors="coerce")

        df["Target (Unit)"] = df["Target (Year)"] / 12
        df["Target (Value)"] = df["Target (Unit)"] * df["Sales Price"]

        all_data.append(df)

    return pd.concat(all_data, ignore_index=True)


# =====================================================
# 📈 HARKAH
# =====================================================
def load_haraka():

    df = pd.read_excel("Rep Harakah.xlsx")
    df = df.replace(r'^\s*$', pd.NA, regex=True)

    first_col = df.columns[0]

    df[first_col] = df[first_col].astype(str)

    df = df[
        df[first_col].notna() &
        (df[first_col].str.strip() != "") &
        (~df[first_col].str.contains("كود الفرع|كود المندوب", na=False))
    ]

    return df


# =====================================================
# ⏳ OVERDUE
# =====================================================
def load_overdue(codes):

    overdue = pd.read_excel("Overdue.xlsx")

    overdue.columns = [
        "Client Name","Client Code","30","60","90","120","150","150+","Balance"
    ]

    overdue["Overdue"] = overdue["120"] + overdue["150"] + overdue["150+"]

    overdue["Rep Code"] = None

    overdue["Rep Code"] = pd.to_numeric(overdue["Rep Code"], errors="coerce")

    overdue = overdue.merge(codes, on="Rep Code", how="left")

    return overdue


# =====================================================
# 👤 CLIENT HARAKAH (NEW ADD)
# =====================================================
def load_client_harakah():

    file_path = "Client Harakah.xlsx"

    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()

    df = df.rename(columns={
        df.columns[0]: "Client Code",
        df.columns[1]: "Client Name",
        df.columns[2]: "Opening Balance",
        df.columns[3]: "Sales Value",
        df.columns[4]: "Returns Value",
        df.columns[5]: "Credit",
        df.columns[6]: "Collection",
        df.columns[7]: "Payments",
        df.columns[8]: "Debit",
        df.columns[9]: "End Balance",
    })

    num_cols = df.columns[2:]
    df[num_cols] = df[num_cols].apply(pd.to_numeric, errors="coerce").fillna(0)

    return df
