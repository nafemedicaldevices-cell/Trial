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

        months = ["Jan","Feb","Mar","Apr","May","Jun",
                  "Jul","Aug","Sep","Oct","Nov","Dec"]

        df_long = df.loc[df.index.repeat(12)].copy()
        df_long["Month"] = months * len(df)

        df_long["Target (Unit)"] = df["Target (Unit)"].repeat(12).values
        df_long["Target (Value)"] = df["Target (Value)"].repeat(12).values

        all_data.append(df_long)

    return pd.concat(all_data, ignore_index=True)


# =========================
# 📂 REP HARKA
# =========================
def load_haraka():

    df = pd.read_excel("Rep Harakah.xlsx")

    df = df.replace(r'^\s*$', pd.NA, regex=True)

    first_col = df.columns[0]
    df[first_col] = df[first_col].astype(str)

    df = df[
        df[first_col].notna() &
        (df[first_col].str.strip() != "") &
        (~df[first_col].str.contains("كود الفرع", na=False)) &
        (~df[first_col].str.contains("كود المندوب", na=False))
    ]

    cols = df.columns.tolist()
    seen = {}
    new_cols = []

    for c in cols:
        if c in seen:
            seen[c] += 1
            new_cols.append(f"{c}_{seen[c]}")
        else:
            seen[c] = 0
            new_cols.append(c)

    df.columns = new_cols

    df = df.rename(columns={
        df.columns[0]: "Rep Code",
        df.columns[1]: "Rep Name",
        df.columns[2]: "Opening Balance",
        df.columns[3]: "Sales Value",
        df.columns[4]: "Returns Value",
        df.columns[5]: "Credit",
        df.columns[6]: "Total Collection",
        df.columns[7]: "Madfoaat",
        df.columns[8]: "Debit",
        df.columns[9]: "End Balance",
        df.columns[10]: "Motalbet El Fatrah",
    })

    return df


# =========================
# 📂 CLIENTS HARKA (FIXED SAFE)
# =========================
def load_client_haraka():

    # 🔴 مهم جدًا: تأكد الاسم في المشروع
    try:
        df = pd.read_excel("Clients Harakah.xlsx")
    except FileNotFoundError:
        return pd.DataFrame({"Error": ["Clients Harakah.xlsx not found"]})

    df = df.replace(r'^\s*$', pd.NA, regex=True)

    first_col = df.columns[0]
    df[first_col] = df[first_col].astype(str)

    df = df[df[first_col].notna() & (df[first_col].str.strip() != "")]

    # fix duplicate columns
    cols = df.columns.tolist()
    seen = {}
    new_cols = []

    for c in cols:
        if c in seen:
            seen[c] += 1
            new_cols.append(f"{c}_{seen[c]}")
        else:
            seen[c] = 0
            new_cols.append(c)

    df.columns = new_cols

    # =========================
    # 🔥 EXTRACT REP CODE
    # =========================
    rep_col = df.columns[3]  # عمود مندوب المبيعات

    df["Rep Code"] = df[rep_col].astype(str).str.extract(r"(\d+)")
    df["Rep Code"] = pd.to_numeric(df["Rep Code"], errors="coerce")

    # =========================
    # 🔗 JOIN REP NAME
    # =========================
    rep_master = pd.read_excel("Rep Harakah.xlsx")[["Rep Code", "Rep Name"]].drop_duplicates()

    df = df.merge(rep_master, on="Rep Code", how="left")

    df["Rep Name"] = df["Rep Name"].fillna("Unknown")

    return df
