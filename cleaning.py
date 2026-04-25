import pandas as pd
import numpy as np
import os

# =========================
# 📂 TARGET FILES
# =========================
FILES = {
    "Rep": "Target Rep.xlsx",
    "Manager": "Target Manager.xlsx",
    "Area": "Target Area.xlsx",
    "Supervisor": "Target Supervisor.xlsx",
    "Evak": "Target Evak.xlsx",
}

# =========================
# 🎯 LOAD TARGETS
# =========================
def load_targets():

    all_data = []

    for level, file in FILES.items():

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
            df_long["Level"] = level

            all_data.append(df_long)

    return pd.concat(all_data, ignore_index=True)


# =========================
# 💰 LOAD SALES / HARAKA
# =========================
def load_haraka():

    df = pd.read_excel("Rep Harakah.xlsx")

    df = df.dropna(how="all").reset_index(drop=True)

    # remove header/text rows
    df = df[~df.astype(str).apply(
        lambda row: row.str.contains("كود", na=False)
    ).any(axis=1)]

    df = df.reset_index(drop=True)

    # 🔥 FORCE STRUCTURE (stable mapping)
    df = df.iloc[:, :11]

    df.columns = [
        "Rep Code","Old Rep Name","Opening Balance",
        "Sales Value","Returns Value",
        "Credit","Total Collection",
        "Cash","Debit","End Balance","Target"
    ]

    # numeric clean
    for col in df.columns[2:]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["Rep Code"] = df["Rep Code"].astype(str).str.strip()

    return df


# =========================
# 📊 OVERDUE
# =========================
def load_overdue(overdue_path, codes):

    overdue = pd.read_excel(overdue_path)

    overdue.columns = [
        "Client Name","Client Code",
        "30 Days","60 Days","90 Days",
        "120 Days","150 Days",
        "More Than 150 Days","Balance"
    ]

    overdue["Rep Code"] = None
    overdue["Old Rep Name"] = None

    mask = overdue["Client Name"].astype(str).str.strip() == "كود المندوب"

    overdue.loc[mask, "Rep Code"] = overdue.loc[mask, "Client Code"]
    overdue.loc[mask, "Old Rep Name"] = overdue.loc[mask, "30 Days"]

    overdue[["Rep Code","Old Rep Name"]] = overdue[["Rep Code","Old Rep Name"]].ffill()

    overdue = overdue.dropna(subset=["Client Name"])

    num_cols = [
        "30 Days","60 Days","90 Days",
        "120 Days","150 Days","More Than 150 Days"
    ]

    for col in num_cols:
        overdue[col] = pd.to_numeric(overdue[col], errors="coerce").fillna(0)

    overdue["Rep Code"] = overdue["Rep Code"].astype(str).str.strip()
    overdue["Client Code"] = overdue["Client Code"].astype(str).str.strip()

    overdue["Overdue"] = (
        overdue["120 Days"] +
        overdue["150 Days"] +
        overdue["More Than 150 Days"]
    )

    codes["Rep Code"] = codes["Rep Code"].astype(str).str.strip()

    return overdue.merge(codes, on="Rep Code", how="left")


# =========================
# 👤 CLIENT HARAKA
# =========================
def load_client_haraka():

    df = pd.read_excel("Client Harakah.xlsx", header=None)

    df = df.dropna(how="all").reset_index(drop=True)

    rep_mask = df.astype(str).apply(
        lambda row: row.str.contains("مندوب المبيعات", na=False)
    ).any(axis=1)

    rep_row = df[rep_mask]

    if not rep_row.empty:
        rep_code = str(rep_row.iloc[0, 4]).strip()
        rep_name = str(rep_row.iloc[0, 5]).strip()
    else:
        rep_code, rep_name = "", ""

    df = df[~rep_mask].reset_index(drop=True)

    df = df.iloc[:, :11]

    df.columns = [
        "Client Code","Client Name","Opening Balance",
        "Sales Value","Returns Value",
        "Credit","Total Collection",
        "Cash","Debit","End Balance","Target"
    ]

    for col in df.columns[2:]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["Rep Code"] = rep_code
    df["Client Code"] = df["Client Code"].astype(str).str.strip()
    df["Old Rep Name"] = rep_name

    if os.path.exists("Code.xlsx"):
        codes = pd.read_excel("Code.xlsx")
        codes.columns = codes.columns.str.strip()
        codes["Rep Code"] = codes["Rep Code"].astype(str).str.strip()

        df = df.merge(codes, on="Rep Code", how="left")

    return df
