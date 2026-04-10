def build_target_pipeline(df, id_name, mapping):

    df = df.copy()
    mapping = mapping.copy()

    # =====================
    # CLEAN COLUMNS
    # =====================
    df.columns = df.columns.str.strip().str.replace(r"\s+", " ", regex=True)

    fixed_cols = ["Year", "Product Code", "Old Product Name", "Sales Price"]
    fixed_cols = [c for c in fixed_cols if c in df.columns]

    dynamic_cols = [c for c in df.columns if c not in fixed_cols]

    # =====================
    # MELT
    # =====================
    df = df.melt(
        id_vars=fixed_cols,
        value_vars=dynamic_cols,
        var_name=id_name,
        value_name="Target (Unit)"
    )

    # =====================
    # CLEAN IDS
    # =====================
    df[id_name] = (
        df[id_name].astype(str)
        .str.replace(r"[^0-9]", "", regex=True)
    )

    df[id_name] = pd.to_numeric(df[id_name], errors="coerce")
    df["Product Code"] = pd.to_numeric(df.get("Product Code"), errors="coerce")

    mapping["Product Code"] = pd.to_numeric(mapping["Product Code"], errors="coerce")

    # =====================
    # CLEAN MAPPING
    # =====================
    mapping = mapping.drop_duplicates("Product Code")

    if "Product Name" in mapping.columns:
        use_cols = ["Product Code", "Product Name"]
    else:
        use_cols = ["Product Code"]

    # =====================
    # MERGE SAFE
    # =====================
    df = df.merge(mapping[use_cols], on="Product Code", how="left")

    # =====================
    # CALCULATION
    # =====================
    df["Target (Unit)"] = pd.to_numeric(df["Target (Unit)"], errors="coerce").fillna(0)
    df["Sales Price"] = pd.to_numeric(df["Sales Price"], errors="coerce").fillna(0)

    df["Full Target Value"] = df["Target (Unit)"] * df["Sales Price"]

    # =====================
    # OUTPUT
    # =====================
    return {
        "value_full": df.groupby([id_name], as_index=False)["Full Target Value"].sum(),
        "raw": df
    }
