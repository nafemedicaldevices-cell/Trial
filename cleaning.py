import pandas as pd

# =========================
# 📊 TARGETS
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

        required_cols = ["Year", "Product Code", "Old Product Name", "Sales Price"]

        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            print(f"❌ Missing in {level}: {missing}")
            continue

        df = df.melt(
            id_vars=required_cols,
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

    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()


# =========================
# 📊 HARKA
# =========================
def load_haraka():

    df = pd.read_excel("Rep Harakah.xlsx")
    df.columns = df.columns.str.strip()

    df = df.replace(r'^\s*$', pd.NA, regex=True)

    first_col = df.columns[0]

    df[first_col] = df[first_col].astype(str)

    df = df[
        df[first_col].notna() &
        (df[first_col].str.strip() != "") &
        (~df[first_col].str.contains("كود الفرع|كود المندوب", na=False))
    ]

    df = df.rename(columns={
        df.columns[0]: "Rep Code",
        df.columns[1]: "Rep Name",
        df.columns[2]: "Opening Balance",
        df.columns[3]: "Sales Value",
        df.columns[4]: "Returns Value",
        df.columns[5]: "Total Collection",
        df.columns[6]: "End Balance",
        df.columns[7]: "Motalbet El Fatrah",
    })

    return df


# =========================
# 📊 SALES (SMART FIX - NO KEYERROR)
# =========================
def load_sales():

    sales = pd.read_excel("Sales.xlsx")
    sales.columns = sales.columns.str.strip()

    # =========================
    # 🔥 AUTO DETECT DATE COLUMN
    # =========================
    date_col = None
    for c in sales.columns:
        if "date" in c.lower() or "تاريخ" in c:
            date_col = c
            break

    if date_col is None:
        raise ValueError("❌ Date column not found in Sales file")

    # =========================
    # CLEAN
    # =========================
    sales = sales.replace(r'^\s*$', pd.NA, regex=True)

    sales = sales[
        sales[date_col].notna() &
        (sales[date_col].astype(str).str.strip() != '')
    ].copy()

    # =========================
    # NUMERIC SAFE
    # =========================
    possible_num_cols = [
        "Sales Unit Before Edit",
        "Returns Unit Before Edit",
        "Sales Price",
        "Invoice Discounts"
    ]

    for c in possible_num_cols:
        if c in sales.columns:
            sales[c] = pd.to_numeric(sales[c], errors="coerce").fillna(0)

    # =========================
    # CALCULATION
    # =========================
    if "Sales Unit Before Edit" in sales.columns and "Sales Price" in sales.columns:
        sales["Total Sales Value"] = sales["Sales Unit Before Edit"] * sales["Sales Price"]

    if "Returns Unit Before Edit" in sales.columns and "Sales Price" in sales.columns:
        sales["Returns Value"] = sales["Returns Unit Before Edit"] * sales["Sales Price"]

    if "Total Sales Value" in sales.columns and "Returns Value" in sales.columns:
        sales["Net Sales Value"] = sales["Total Sales Value"] - sales["Returns Value"]

    return sales
