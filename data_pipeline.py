def clean_sales(sales, mapping, codes):

    sales.columns = sales.columns.str.strip()

    # =========================
    # CREATE COLUMN SAFELY (FIX)
    # =========================
    if "Old Product Code" not in sales.columns:
        sales["Old Product Code"] = np.nan

    if "Old Product Name" not in sales.columns:
        sales["Old Product Name"] = np.nan

    # =========================
    # TRY EXTRACT ONLY IF COLUMN EXISTS
    # =========================
    if "Date" in sales.columns and "Warehouse Name" in sales.columns:

        mask = sales["Date"].astype(str).str.strip().eq("كود الصنف")

        sales.loc[mask, "Old Product Code"] = sales.loc[mask, "Warehouse Name"]
        sales.loc[mask, "Old Product Name"] = sales.loc[mask, "Client Code"]

        sales[["Old Product Code","Old Product Name"]] = sales[
            ["Old Product Code","Old Product Name"]
        ].ffill()

    # =========================
    # SAFE CONVERSION (FIX KEYERROR)
    # =========================
    if "Old Product Code" not in sales.columns:
        sales["Old Product Code"] = np.nan

    sales["Old Product Code"] = pd.to_numeric(sales["Old Product Code"], errors="coerce")

    if "Rep Code" in sales.columns:
        sales["Rep Code"] = pd.to_numeric(sales["Rep Code"], errors="coerce")
    else:
        sales["Rep Code"] = np.nan

    # =========================
    # MERGE SAFELY
    # =========================
    if mapping is not None:
        sales = sales.merge(mapping, on="Old Product Code", how="left")

    if codes is not None:
        sales = sales.merge(codes, on="Rep Code", how="left")

    # =========================
    # KPI
    # =========================
    if "Sales Unit Before Edit" in sales.columns and "Sales Price" in sales.columns:
        sales["Total Sales Value"] = sales["Sales Unit Before Edit"] * sales["Sales Price"]
    else:
        sales["Total Sales Value"] = 0

    if "Returns Unit Before Edit" in sales.columns and "Sales Price" in sales.columns:
        sales["Returns Value"] = sales["Returns Unit Before Edit"] * sales["Sales Price"]
    else:
        sales["Returns Value"] = 0

    sales["Sales After Returns"] = sales["Total Sales Value"] - sales["Returns Value"]

    return sales
