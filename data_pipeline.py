def build_target_pipeline(df, id_name, mapping):

    df = df.copy()
    mapping = mapping.copy()

    df.columns = df.columns.str.strip()

    fixed_cols = [c for c in ["Year", "Product Code", "Old Product Name", "Sales Price"] if c in df.columns]
    dynamic_cols = [c for c in df.columns if c not in fixed_cols]

    df = df.melt(
        id_vars=fixed_cols,
        value_vars=dynamic_cols,
        var_name=id_name,
        value_name="Target (Unit)"
    )

    # clean
    df[id_name] = pd.to_numeric(df[id_name].astype(str).str.replace(r"[^0-9]", "", regex=True), errors="coerce")
    df["Product Code"] = pd.to_numeric(df["Product Code"], errors="coerce")
    mapping["Product Code"] = pd.to_numeric(mapping["Product Code"], errors="coerce")

    mapping = mapping.drop_duplicates("Product Code")
    df = df.merge(mapping, on="Product Code", how="left")

    df["Target (Unit)"] = pd.to_numeric(df["Target (Unit)"], errors="coerce").fillna(0)
    df["Sales Price"] = pd.to_numeric(df["Sales Price"], errors="coerce").fillna(0)

    df["Full Value"] = df["Target (Unit)"] * df["Sales Price"]

    # =========================
    # KPI LOGIC
    # =========================
    full = df.copy()

    month = df.copy()
    month["Value"] = full["Full Value"] * (current_month / 12)

    ytd = df.copy()
    ytd["Value"] = full["Full Value"] * (current_month / 12)

    quarter = df.copy()
    quarter["Value"] = full["Full Value"] * (past_quarters / 4)

    full["Value"] = full["Full Value"]

    # =========================
    # VALUE TABLE
    # =========================
    def group(d):
        return d.groupby([id_name], as_index=False)["Value"].sum()

    value_table = group(full).rename(columns={"Value": "Full"})
    value_table["Month"] = group(month)["Value"]
    value_table["Quarter"] = group(quarter)["Value"]
    value_table["YTD"] = group(ytd)["Value"]

    # =========================
    # PRODUCTS TABLE (FIXED 🚀)
    # =========================
    def product_group(d):
        return d.groupby(
            [id_name, "Product Code", "Product Name"],
            as_index=False
        )["Value"].sum()

    products_full = product_group(full)
    products_month = product_group(month)
    products_quarter = product_group(quarter)
    products_ytd = product_group(ytd)

    return {
        "value_table": value_table,

        # PRODUCTS FULL KPI SET 🔥
        "products_full": products_full,
        "products_month": products_month,
        "products_quarter": products_quarter,
        "products_ytd": products_ytd,
    }
