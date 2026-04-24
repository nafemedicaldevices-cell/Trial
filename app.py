import pandas as pd

def export_all_excel(targets, haraka, sales, file_name="KPI_FULL_REPORT.xlsx"):

    with pd.ExcelWriter(file_name, engine="openpyxl") as writer:

        # =========================
        # TARGETS
        # =========================
        targets.to_excel(writer, sheet_name="Targets", index=False)

        # =========================
        # HARKA
        # =========================
        haraka.to_excel(writer, sheet_name="Harakah", index=False)

        # =========================
        # SALES
        # =========================
        sales.to_excel(writer, sheet_name="Sales", index=False)

        # =========================
        # COMBINED VIEW
        # =========================
        targets_c = targets.copy()
        targets_c["Source"] = "Targets"

        haraka_c = haraka.copy()
        haraka_c["Source"] = "Harakah"

        sales_c = sales.copy()
        sales_c["Source"] = "Sales"

        combined = pd.concat([targets_c, haraka_c, sales_c], ignore_index=True, sort=False)

        combined.to_excel(writer, sheet_name="Combined", index=False)

    return file_name
