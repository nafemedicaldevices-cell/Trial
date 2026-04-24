# =========================
# 🚀 SALES KPI
# =========================
def build_sales_pipeline(sales, codes):

    sales = sales.merge(codes, on="Rep Code", how="inner")

    sales["Total Sales Value"] = sales["Sales Unit Before Edit"] * sales["Sales Price"]
    sales["Returns Value"] = sales["Returns Unit Before Edit"] * sales["Sales Price"]
    sales["Sales After Returns"] = sales["Total Sales Value"] - sales["Returns Value"]

    return sales.groupby("Rep Code", as_index=False)[
        ["Total Sales Value","Returns Value","Sales After Returns"]
    ].sum()


# =========================
# 📦 OPENING KPI
# =========================
def build_opening_pipeline(opening, codes):

    opening["Total Collection"] = opening["Cash Collection"] + opening["Collection Checks"]
    opening["Sales After Returns"] = opening["Total Sales"] - opening["Returns"]
    opening["Opening KPI"] = opening["Sales After Returns"] + opening["Total Collection"]

    opening = opening.merge(codes, on="Rep Code", how="left")

    return opening.groupby("Rep Code", as_index=False)[
        ["Sales After Returns","Total Collection","Opening KPI"]
    ].sum()


# =========================
# ⏳ OVERDUE KPI
# =========================
def build_overdue_pipeline(overdue, codes):

    overdue["Overdue Value"] = (
        overdue["120 Days"] +
        overdue["150 Days"] +
        overdue["More Than 150 Days"]
    )

    overdue = overdue.merge(codes, on="Rep Code", how="left")

    return overdue.groupby("Rep Code", as_index=False)[
        ["Overdue Value"]
    ].sum()
