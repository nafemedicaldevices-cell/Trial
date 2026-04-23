import pandas as pd
import numpy as np

# =========================
# 📂 FILES
# =========================
TARGET_FILES = {
    "Manager": "Target Manager.xlsx",
    "Area": "Target Area.xlsx",
    "Supervisor": "Target Supervisor.xlsx",
    "Evak": "Target Evak.xlsx",
}

REP_FILE = "Target Rep.xlsx"

# =========================
# 📊 TARGET CLEANING
# =========================
def clean_target(file, level):

    df = pd.read_excel(file, sheet_name=0)
    df.columns = df.columns.str.strip()

    fixed_cols = [
        "Year",
        "Product Code",
        "Old Product Name",
        "Sales Price"
    ]

    df = df.melt(
        id_vars=fixed_cols,
        var_name="Code",
        value_name="Target (Year)"
    )

    df["Level"] = level
    df["Target (Year)"] = pd.to_numeric(df["Target (Year)"], errors="coerce")

    df["Target (Unit)"] = df["Target (Year)"] / 12
    df["Target (Value)"] = df["Target (Unit)"] * df["Sales Price"]

    months = [
        "Jan","Feb","Mar","Apr","May","Jun",
        "Jul","Aug","Sep","Oct","Nov","Dec"
    ]

    df_long = df.loc[df.index.repeat(12)].copy()
    df_long["Month"] = np.tile(months, len(df))

    df_long["Target (Unit)"] = np.repeat(df["Target (Unit)"].values, 12)
    df_long["Target (Value)"] = np.repeat(df["Target (Value)"].values, 12)

    return df_long


# =========================
# 📊 REP CLEANING
# =========================
def clean_rep(file):

    df = pd.read_excel(file, sheet_name="Rep Harakah")
    df.columns = df.columns.str.strip()

    df = df.iloc[2:].reset_index(drop=True)
    df = df.dropna(how="all")

    if "Rep Code" in df.columns:
        df = df[df["Rep Code"].notna()]

    df["Level"] = "Rep"

    if "Target (Year)" not in df.columns:
        return None

    df["Target (Year)"] = pd.to_numeric(df["Target (Year)"], errors="coerce")

    df["Target (Unit)"] = df["Target (Year)"] / 12
    df["Target (Value)"] = df["Target (Unit)"] * df["Sales Price"]

    months = [
        "Jan","Feb","Mar","Apr","May","Jun",
        "Jul","Aug","Sep","Oct","Nov","Dec"
    ]

    df_long = df.loc[df.index.repeat(12)].copy()
    df_long["Month"] = np.tile(months, len(df))

    df_long["Target (Unit)"] = np.repeat(df["Target (Unit)"].values, 12)
    df_long["Target (Value)"] = np.repeat(df["Target (Value)"].values, 12)

    return df_long


# =========================
# 📊 MAIN FUNCTION
# =========================
def load_and_process_data():

    all_data = []

    # TARGET FILES
    for level, file in TARGET_FILES.items():
        df = clean_target(file, level)
        all_data.append(df)

    # REP FILE
    rep_df = clean_rep(REP_FILE)
    if rep_df is not None:
        all_data.append(rep_df)

    return pd.concat(all_data, ignore_index=True)
