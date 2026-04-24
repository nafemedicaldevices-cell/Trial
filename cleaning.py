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
# 📊 HARKA
# =========================
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

    df.columns = df.columns.str.strip()

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
# 📊 SALES (CLEAN ONLY)
# =========================
def load_sales(sales):

    sales.columns = sales.columns.str.strip()

    sales = sales.replace(r'^\s*$', pd.NA, regex=True)

    sales = sales[
        sales['Date'].notna() &
        (sales['Date'].astype(str).str.strip() != '') &
        (~sales['Date'].astype(str).str.contains('المندوب|كود الفرع|كود الصنف', na=False))
    ].copy()

    num_cols = [
        'Sales Unit Before Edit',
        'Returns Unit Before Edit',
        'Sales Price',
        'Invoice Discounts'
    ]

    sales[num_cols] = sales[num_cols].apply(pd.to_numeric, errors='coerce').fillna(0)

    sales['Total Sales Value'] = sales['Sales Unit Before Edit'] * sales['Sales Price']
    sales['Returns Value'] = sales['Returns Unit Before Edit'] * sales['Sales Price']
    sales['Net Sales Value'] = sales['Total Sales Value'] - sales['Returns Value']

    return sales
