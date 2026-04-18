def build_final_layer(cleaned, linking):

    final = {}

    # =========================
    # TARGET KPI
    # =========================
    final["target_rep"] = build_target_pipeline(
        cleaned["target_rep"],
        "Rep Code",
        cleaned["mapping"]
    )["value_table"]

    final["target_manager"] = build_target_pipeline(
        cleaned["target_manager"],
        "Manager Code",
        cleaned["mapping"]
    )["value_table"]

    final["target_area"] = build_target_pipeline(
        cleaned["target_area"],
        "Area Code",
        cleaned["mapping"]
    )["value_table"]

    final["target_supervisor"] = build_target_pipeline(
        cleaned["target_supervisor"],
        "Supervisor Code",
        cleaned["mapping"]
    )["value_table"]

    # =========================
    # PRODUCTS KPI (مثال Rep)
    # =========================
    final["products_rep"] = build_target_pipeline(
        cleaned["target_rep"],
        "Rep Code",
        cleaned["mapping"]
    )["products_full"]

    # =========================
    # SALES KPI
    # =========================
    sales = build_sales_pipeline(cleaned["sales"], cleaned["codes"])
    final["sales_rep"] = sales["rep"]
    final["sales_manager"] = sales["manager"]
    final["sales_area"] = sales["area"]
    final["sales_supervisor"] = sales["supervisor"]

    # =========================
    # OPENING KPI
    # =========================
    opening = build_opening_pipeline(cleaned["opening"], cleaned["codes"])
    final["opening_rep"] = opening["rep"]
    final["opening_manager"] = opening["manager"]
    final["opening_area"] = opening["area"]
    final["opening_supervisor"] = opening["supervisor"]

    # =========================
    # OVERDUE KPI
    # =========================
    overdue = build_overdue_pipeline(cleaned["overdue"], cleaned["codes"])
    final["overdue_rep"] = overdue["rep"]
    final["overdue_manager"] = overdue["manager"]
    final["overdue_area"] = overdue["area"]
    final["overdue_supervisor"] = overdue["supervisor"]

    return final
