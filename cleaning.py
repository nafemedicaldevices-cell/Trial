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

def load_targets():

    targets = {}

    for level, file in FILES.items():

        sheets = pd.read_excel(file, sheet_name=None)

        level_data = []

        for sheet_name, df in sheets.items():

            df.columns = df.columns.str.strip()

            fixed_cols = ["Year", "Product Code", "Old Product Name", "Sales Price"]

            df = df.melt(
                id_vars=fixed_cols,
                var_name="Code",
                value_name="Target (Year)"
            )

            df["Target (Year)"] = pd.to_numeric(
                df["Target (Year)"], errors="coerce"
            )

            df["Target (Unit)"] = df["Target (Year)"] / 12
            df["Target (Value)"] = df["Target (Unit)"] * df["Sales Price"]

            months = [
                "Jan","Feb","Mar","Apr","May","Jun",
                "Jul","Aug","Sep","Oct","Nov","Dec"
            ]

            df_long = df.loc[df.index.repeat(12)].copy()

            df_long["Month"] = months * len(df)

            df_long["Target (Unit)"] = (
                df["Target (Unit)"].repeat(12).values
            )

            df_long["Target (Value)"] = (
                df["Target (Value)"].repeat(12).values
            )

            # 🔥 توحيد الكود كـ string
            df_long["Code"] = df_long["Code"].astype(str).str.strip()

            df_long["Level"] = level

            level_data.append(df_long)

        targets[level] = pd.concat(
            level_data,
            ignore_index=True
        )

    return targets


# =========================
# 📂 REP HARKAH
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
        df.columns[1]: "Old Rep Name",
        df.columns[2]: "Opening Balance",
        df.columns[3]: "Sales Value",
        df.columns[4]: "Returns Value",
        df.columns[5]: "Tasweyat Madinah (Credit)",
        df.columns[6]: "Total Collection",
        df.columns[7]: "Madfoaat",
        df.columns[8]: "Tasweyat Madinah (Debit)",
        df.columns[9]: "End Balance",
        df.columns[10]: "Motalbet El Fatrah",
    })

    # 🔥 توحيد Rep Code
    df["Rep Code"] = df["Rep Code"].astype(str).str.strip()

    return df


# =========================
# 📂 OVERDUE
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

    mask = (
        overdue["Client Name"]
        .astype(str)
        .str.strip()
        == "كود المندوب"
    )

    overdue.loc[mask, "Rep Code"] = overdue.loc[mask, "Client Code"]
    overdue.loc[mask, "Old Rep Name"] = overdue.loc[mask, "30 Days"]

    overdue[["Rep Code","Old Rep Name"]] = (
        overdue[["Rep Code","Old Rep Name"]].ffill()
    )

    overdue = overdue[
        overdue["Client Name"].notna() &
        (overdue["Client Name"].astype(str).str.strip() != '') &
        (~overdue["Client Name"].astype(str).str.contains(
            "اجمال|كود الفرع|كود المندوب|اسم العميل",
            na=False
        ))
    ].copy()

    num_cols = [
        "30 Days","60 Days","90 Days",
        "120 Days","150 Days",
        "More Than 150 Days"
    ]

    for col in num_cols:
        overdue[col] = pd.to_numeric(
            overdue[col],
            errors="coerce"
        ).fillna(0)

    # 🔥 توحيد الأكواد كـ string
    overdue["Rep Code"] = overdue["Rep Code"].astype(str).str.strip()
    overdue["Client Code"] = overdue["Client Code"].astype(str).str.strip()

    overdue["Overdue"] = (
        overdue["120 Days"]
        + overdue["150 Days"]
        + overdue["More Than 150 Days"]
    )

    # codes
    codes["Rep Code"] = codes["Rep Code"].astype(str).str.strip()

    overdue = overdue.merge(
        codes,
        on="Rep Code",
        how="left"
    )

    return overdue


# =========================
# 👤 CLIENT HARKAH
# =========================
def load_client_haraka():

    file_path = "Client Harakah.xlsx"
    code_path = "Code.xlsx"

    df = pd.read_excel(file_path, header=None)

    # استخراج المندوب
    rep_mask = df.astype(str).apply(
        lambda row: row.str.contains("مندوب المبيعات", na=False)
    ).any(axis=1)

    rep_row = df[rep_mask]

    if not rep_row.empty:
        r = rep_row.iloc[0]
        rep_code = r.iloc[4]
        rep_name = r.iloc[5]
    else:
        rep_code = np.nan
        rep_name = ""

    df = df[~rep_mask].reset_index(drop=True)

    df.columns = [
        "Client Code","Client Name","Opening Balance",
        "Sales Value","Returns Value",
        "Tasweyat Madinah (Credit)","Total Collection",
        "Madfoaat","Tasweyat Madinah (Debit)",
        "End Balance","Motalbet El Fatrah"
    ]

    df = df[
        ~df.astype(str).apply(
            lambda row: row.str.contains("كود العميل", na=False)
        ).any(axis=1)
    ].copy()

    first_col = df.columns[0]

    df[first_col] = df[first_col].astype(str)

    df = df[
        (df[first_col].notna()) &
        (df[first_col].str.strip() != "") &
        (~df[first_col].str.lower().isin(["none","nan"]))
    ].copy()

    df = df.reset_index(drop=True)

    # تحويل أرقام
    for col in df.columns[2:]:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        ).fillna(0)

    # 🔥 توحيد الأكواد
    df["Rep Code"] = str(rep_code).strip()
    df["Client Code"] = df["Client Code"].astype(str).str.strip()
    df["Old Rep Name"] = rep_name

    # Merge codes
    if os.path.exists(code_path):

        codes = pd.read_excel(code_path)
        codes.columns = codes.columns.str.strip()

        codes["Rep Code"] = codes["Rep Code"].astype(str).str.strip()

        df = df.merge(
            codes,
            on="Rep Code",
            how="left"
        )

    return df
