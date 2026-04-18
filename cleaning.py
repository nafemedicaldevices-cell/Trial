def build_cleaning_layer(data):

    cleaned = {}

    # =========================
    # SALES CLEANING
    # =========================
    cleaned["sales"] = fix_sales_columns(data["sales"])

    # =========================
    # TARGET CLEANING (بدون أي حسابات)
    # =========================
    cleaned["target_rep"] = data["target_rep"].copy()
    cleaned["target_manager"] = data["target_manager"].copy()
    cleaned["target_area"] = data["target_area"].copy()
    cleaned["target_supervisor"] = data["target_supervisor"].copy()
    cleaned["target_evak"] = data["target_evak"].copy()

    # =========================
    # SUPPORT TABLES CLEANING
    # =========================
    cleaned["mapping"] = data["mapping"].drop_duplicates()
    cleaned["codes"] = data["codes"].drop_duplicates()

    cleaned["opening"] = data["opening"].copy()
    cleaned["overdue"] = data["overdue"].copy()

    return cleaned
