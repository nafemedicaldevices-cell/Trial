import pandas as pd
import numpy as np
import os

# =========================
# 📂 LOAD EXCEL SAFELY
# =========================
def load_excel(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing file: {path}")
    return pd.read_excel(path)


# =========================
# 📂 CLIENT HARAKAH
# =========================
def load_client_haraka():

    df = load_excel("Client Harakah.xlsx")

    df = df.replace(r'^\s*$', np.nan, regex=True)

    first_col = df.columns[0]
    df[first_col] = df[first_col].astype(str)

    df = df[
        df[first_col].notna() &
        (df[first_col].str.strip() != "") &
        (~df[first_col].str.contains("كود العميل", na=False))
    ]

    df.columns = [
        "Client Code","Client Name","Opening Balance",
        "Sales Value","Returns Value",
        "Credit","Total Collection","Madfoaat",
        "Debit","End Balance","Motalbet"
    ]

    num_cols = df.columns[2:]
    df[num_cols] = df[num_cols].apply(pd.to_numeric, errors="coerce").fillna(0)

    return df


# =========================
# 📂 TARGETS
# =========================
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

        df = load_excel(file)
        df.columns = df.columns.str.strip()

        fixed = ["Year", "Product Code", "Old Product Name", "Sales Price"]

        df = df.melt(
            id_vars=fixed,
            var_name="Code",
            value_name="Target (Year)"
        )

        df["Level"] = level
        df["Target (Year)"] = pd.to_numeric(df["Target (Year)"], errors="coerce")

        df["Target (Unit)"] = df["Target (Year)"] / 12
        df["Target (Value)"] = df["Target (Unit)"] * df["Sales Price"]

        months = ["Jan","Feb","Mar","Apr","May","Jun",
                  "Jul","Aug","Sep","Oct","Nov","Dec"]

        df_long = df.loc[df.index.repeat(12)].copy()
        df_long["Month"] = months * len(df)

        df_long["Target (Unit)"] = df["Target (Unit)"].repeat(12).values
        df_long["Target (Value)"] = df["Target (Value)"].repeat(12).values

        all_data.append(df_long)

    return pd.concat(all_data, ignore_index=True)


# =========================
# 📂 HARKA
# =========================
def load_haraka():

    df = load_excel("Rep Harakah.xlsx")

    df = df.replace(r'^\s*$', np.nan, regex=True)

    first_col = df.columns[0]

    df = df[
        df[first_col].notna() &
        (~df[first_col].astype(str).str.contains("كود", na=False))
    ]

    df.columns = [
        "Rep Code","Rep Name","Opening",
        "Sales","Returns","Credit",
        "Collection","Payments","Debit",
        "End Balance","Due"
    ]

    num_cols = df.columns[2:]
    df[num_cols] = df[num_cols].apply(pd.to_numeric, errors="coerce").fillna(0)

    return df


# =========================
# 📂 OVERDUE (FIXED ⚡)
# =========================
def load_overdue():

    df = load_excel("Overdue.xlsx")

    df.columns = [
        "Client Name","Client Code","30","60","90","120","150","150+","Balance"
    ]

    # initialize safely as string (IMPORTANT FIX)
    df["Rep Code"] = ""
    df["Rep Name"] = ""

    mask = df["Client Name"].astype(str).str.contains("كود المندوب", na=False)

    # SAFE ASSIGNMENT (FIX TYPEERROR)
    df.loc[mask, "Rep Code"] = df.loc[mask, "Client Code"].astype(str).values
    df.loc[mask, "Rep Name"] = df.loc[mask, "30"].astype(str).values

    df[["Rep Code","Rep Name"]] = df[["Rep Code","Rep Name"]].ffill()

    df = df[
        ~df["Client Name"].astype(str).str.contains(
            "اجمالي|كود الفرع|كود المندوب", na=False
        )
    ]

    num_cols = ["30","60","90","120","150","150+","Client Code"]

    df[num_cols] = df[num_cols].apply(pd.to_numeric, errors="coerce").fillna(0)

    df["Overdue"] = df["120"] + df["150"] + df["150+"]

    return df
