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
    df = df.dropna(how="all")

    df = df[~df.astype(str).apply(
        lambda x: x.str.contains("مندوب المبيعات|صافى مبيعات", na=False)
    ).any(axis=1)]

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
# 📂 CLIENT HARKA (FINAL FIX)
# =========================
def load_client_haraka():

    df = pd.read_excel("Client Harakah.xlsx")

    df = df.replace(r'^\s*$', pd.NA, regex=True)
    df = df.dropna(how="all")

    # ❌ حذف الهيدر العربي داخل الداتا
    df = df[~df.astype(str).apply(
        lambda x: x.str.contains(
            "رصيد افتتاحى|صافى مبيعات|صافى مرتجع مبيعات|تسويات مدينة",
            na=False
        )
    ).any(axis=1)]

    # =========================
    # 🏷️ تثبيت الأعمدة
    # =========================
    df.columns = [
        "Branch",
        "Rep Info",
        "Rep Code Raw",
        "Rep Name Raw",
        "Opening Balance",
        "Sales Value",
        "Returns Value",
        "Tasweyat Madinah",
        "Total Collection",
        "Madfoaat",
        "End Balance"
    ]

    # =========================
    # 👤 استخراج Rep Code + Name
    # =========================
    df["Rep Code"] = df["Rep Code Raw"].astype(str).str.extract(r"(\d+)")
    df["Rep Name"] = df["Rep Name Raw"].astype(str).str.strip()

    # تنظيف الاسم
    df["Rep Name"] = df["Rep Name"].str.replace("باسم", "", regex=True).str.strip()

    # =========================
    # 🔁 Fill Down
    # =========================
    df["Rep Code"] = df["Rep Code"].ffill()
    df["Rep Name"] = df["Rep Name"].ffill()

    df["Rep Code"] = pd.to_numeric(df["Rep Code"], errors="coerce")

    return df
