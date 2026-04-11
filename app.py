    # =========================
    # 📦 PRODUCTS TABLE (FIXED + SAFE)
    # =========================
    def product_group(d):

        cols_needed = [id_name, "Product Code", "Product Name", "Target (Unit)", "Value"]
        cols_needed = [c for c in cols_needed if c in d.columns]

        # حماية لو مفيش Product Name
        if "Product Name" not in d.columns:
            d["Product Name"] = "UNKNOWN"

        return (
            d.groupby(
                [id_name, "Product Code", "Product Name"],
                as_index=False
            )
            .agg(
                Units=("Target (Unit)", "sum"),
                Value=("Value", "sum")
            )
        )

    return {
        "value_table": value_table,

        # ✅ دي اللي كانت ناقصة
        "products_full": product_group(full),
        "products_month": product_group(month),
        "products_quarter": product_group(quarter),
        "products_ytd": product_group(ytd),
    }
