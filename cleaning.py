import pandas as pd

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

def load_targets():

    all_data = []

    months = ["Jan","Feb","Mar","Apr","May","Jun",
              "Jul","Aug","Sep","Oct","Nov","Dec"]

    for level, file in FILES.items():

        df = pd.read_excel(file)
        df.columns = df.columns.str.strip()

        fixed_cols = ["Year", "Product Code", "Old Product Name", "Sales Price"]

        df = df.melt(
            id_vars=fixed_cols,
            var_name="Code",
            value_name="Target (Year)"
        )

        df["Level"] = level
        df["Target (Year)"] = pd.to_numeric(df["Target (Year)"], errors="coerce")

        df["Target (Unit)"] = df["Target (Year)"] / 12
        df["Target (Value)"] = df["Target (Unit)"] * df["Sales Price"]

        df_expanded = df.loc[df.index.repeat(12)].copy()
        df_expanded["Month"] = months * len(df)

        df_expanded["Target (Unit)"] = df["Target (Unit)"].repeat(12).values
        df_expanded["Target (Value)"] = df["Target (Value)"].repeat(12).values

        all_data.append(df_expanded)

    return pd.concat(all_data, ignore_index=True)


# =========================
# 📂 REP HARKA (FIXED FINAL)
# =========================
def load_haraka():

    df = pd.read_excel("Rep Harakah.xlsx")

    df = df.replace(r'^\s*$', pd.NA, regex=True)

    # 🔥 FIX FINAL: handle None / nan / empty
    first_col = df.columns[0]

    df[first_col] = df[first_col].astype(str).str.strip().str.lower()

    df = df[
        ~df[first_col].isin(["", "nan", "none"])
    ]

    df.columns = [
        "Rep Code",
        "Rep Name",
        "Opening Balance",
        "Sales Value",
        "Returns Value",
        "Credit",
        "Total Collection",
        "Madfoaat",
        "Debit",
        "End Balance",
        "Motalbet El Fatrah"
    ]

    return df


# =========================
# 📂 CLIENT HARKA (FIXED FINAL)
# =========================
def load_client_haraka():

    df = pd.read_excel("Client Harakah.xlsx")

    df = df.replace(r'^\s*$', pd.NA, regex=True)

    # 🔥 FIX FINAL: handle None / nan / empty
    first_col = df.columns[0]

    df[first_col] = df[first_col].astype(str).str.strip().str.lower()

    df = df[
        ~df[first_col].isin(["", "nan", "none"])
    ]

    df.columns = [f"Col{i}" for i in range(df.shape[1])]

    rep_row = df[df.astype(str).apply(
        lambda x: x.str.contains("مندوب المبيعات", na=False)
    ).any(axis=1)]

    rep_code = pd.NA
    rep_name = pd.NA

    if not rep_row.empty:
        rep_code = rep_row.iloc[0, 2]
        rep_name = rep_row.iloc[0, 3]

    df["Rep Code"] = rep_code
    df["Rep Name"] = rep_name

    df["Rep Code"] = pd.to_numeric(df["Rep Code"], errors="coerce").ffill()
    df["Rep Name"] = df["Rep Name"].ffill()

    return df
