def build_linking_layer(cleaned):

    linking = {}

    # =========================
    # SALES ↔ CODES LINK
    # =========================
    sales = cleaned["sales"].copy()
    codes = cleaned["codes"].copy()

    sales["Rep Code"] = pd.to_numeric(sales["Rep Code"], errors="coerce")
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")

    linking["sales_linked"] = sales.merge(
        codes,
        on="Rep Code",
        how="inner"
    )

    # =========================
    # MAPPING CHECK LINK
    # =========================
    linking["mapping_linked"] = codes.merge(
        cleaned["mapping"],
        on="Rep Code",
        how="left"
    )

    # =========================
    # TARGET ↔ MAPPING CHECK (اختياري)
    # =========================
    linking["target_mapping"] = cleaned["mapping"].copy()

    return linking
