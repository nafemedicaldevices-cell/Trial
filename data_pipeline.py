import pandas as pd
import numpy as np

# =========================
# 📅 TIME SETTINGS
# =========================
_today          = pd.Timestamp.today()
current_month   = _today.month
current_quarter = (current_month - 1) // 3 + 1
past_quarters   = max(current_quarter - 1, 0)


# =========================
# 📂 LOAD ALL DATA
# =========================
def load_data(base_path: str = ".") -> dict:
    """
    Load every Excel file needed by the dashboard.
    Pass base_path if the files live in a sub-folder, e.g. load_data("data/").
    """
    def p(name):
        return f"{base_path.rstrip('/')}/{name}" if base_path != "." else name

    return {
        # transactional
        "sales":          pd.read_excel(p("Sales.xlsx")),
        "overdue":        pd.read_excel(p("Overdue.xlsx")),
        "extra_discounts":pd.read_excel(p("Extradiscounts.xlsx")),
        "opening":        pd.read_excel(p("Opening.xlsx")),
        "opening_detail": pd.read_excel(p("Opening Detail.xlsx")),

        # targets (one file per hierarchy level)
        "target_manager":    pd.read_excel(p("Target Manager.xlsx")),
        "target_area":       pd.read_excel(p("Target Area.xlsx")),
        "target_rep":        pd.read_excel(p("Target Rep.xlsx")),
        "target_supervisor": pd.read_excel(p("Target Supervisor.xlsx")),
        "target_evak":       pd.read_excel(p("Target Evak.xlsx")),

        # lookup tables
        "mapping": pd.read_excel(p("Mapping.xlsx")),
        "codes":   pd.read_excel(p("Code.xlsx")),
    }


# ─────────────────────────────────────────────
# HELPER — shared numeric / ID cleaning
# ─────────────────────────────────────────────
def _to_num(series, dtype=None):
    out = pd.to_numeric(series, errors="coerce")
    if dtype:
        out = out.astype(dtype)
    return out

def _clean_id(series):
    """Strip non-digit characters then cast to nullable Int64."""
    return _to_num(
        series.astype(str).str.replace(r"[^0-9]", "", regex=True),
        dtype="Int64"
    )


# =========================
# 📦 1 — SALES PIPELINE
# =========================
def build_sales_pipeline(sales: pd.DataFrame,
                         mapping: pd.DataFrame,
                         codes: pd.DataFrame) -> dict:

    sales   = sales.copy()
    mapping = mapping.copy()
    codes   = codes.copy()

    # ── 1a. rename columns ───────────────────
    sales.columns = sales.columns.str.strip()
    expected = [
        "Date", "Warehouse Name", "Client Code", "Client Name", "Notes", "MF",
        "Mostanad", "Rep Code", "Sales Unit Before Edit",
        "Returns Unit Before Edit", "Sales Price",
        "Invoice Discounts", "Sales Value",
    ]
    if len(sales.columns) == len(expected):
        sales.columns = expected

    # ── 1b. extract product codes from header rows ───
    if "Date" in sales.columns:
        mask = sales["Date"].astype(str).str.strip().eq("كود الصنف")

        for col in ("Old Product Code", "Old Product Name"):
            if col not in sales.columns:
                sales[col] = np.nan
            sales[col] = sales[col].astype("object")

        sales.loc[mask, "Old Product Code"] = sales.loc[mask, "Warehouse Name"].astype(str)
        sales.loc[mask, "Old Product Name"] = sales.loc[mask, "Client Code"].astype(str)
        sales[["Old Product Code", "Old Product Name"]] = (
            sales[["Old Product Code", "Old Product Name"]].ffill()
        )

    # ── 1c. drop summary / header rows ───────
    drop_kw = r"المندوب|كود الفرع|تاريخ|كود الصنف"
    sales = sales[sales["Date"].notna()].copy()
    sales = sales[~sales["Date"].astype(str).str.contains(drop_kw, na=False)].copy()
    sales = sales.reset_index(drop=True)

    # ── 1d. numeric columns ───────────────────
    num_cols = [
        "Sales Unit Before Edit", "Returns Unit Before Edit",
        "Sales Price", "Invoice Discounts", "Sales Value",
    ]
    for col in num_cols:
        if col in sales.columns:
            sales[col] = _to_num(sales[col]).fillna(0)

    # ── 1e. ID columns ────────────────────────
    if "Old Product Code" in sales.columns:
        sales["Old Product Code"] = _to_num(sales["Old Product Code"], "Int64")
    if "Rep Code" in sales.columns:
        sales["Rep Code"] = _to_num(sales["Rep Code"], "Int64")

    # ── 1f. merge product mapping ─────────────
    if "Old Product Code" in sales.columns:
        mapping_cols = [c for c in [
            "Old Product Code", "4 Classification", "Product Name",
            "Product Code", "Category", "Next Factor", "2 Classification",
        ] if c in mapping.columns]
        mapping["Old Product Code"] = _to_num(mapping["Old Product Code"], "Int64")
        mapping_clean = mapping[mapping_cols].drop_duplicates("Old Product Code")
        sales = sales.merge(mapping_clean, on="Old Product Code", how="left")

    # ── 1g. merge hierarchy codes ─────────────
    if "Next Factor" not in sales.columns:
        sales["Next Factor"] = 1
    sales["Next Factor"] = sales["Next Factor"].fillna(1)

    codes["Rep Code"] = _to_num(codes["Rep Code"], "Int64")
    sales = sales.merge(codes, on="Rep Code", how="left")

    # ── 1h. computed KPIs ─────────────────────
    sales["Total Sales Value"]  = sales["Sales Unit Before Edit"]    * sales["Sales Price"]
    sales["Returns Value"]      = sales["Returns Unit Before Edit"]  * sales["Sales Price"]
    sales["Sales After Returns"]= sales["Total Sales Value"]         - sales["Returns Value"]
    sales["Net Sales Unit"]     = (
        (sales["Sales Unit Before Edit"] - sales["Returns Unit Before Edit"])
        * sales["Next Factor"]
    )

    # ── 1i. grouped outputs ───────────────────
    val_cols  = ["Total Sales Value", "Returns Value", "Sales After Returns", "Invoice Discounts"]
    prod_cols = ["Sales Value", "Net Sales Unit"]

    def grp(df, by, cols):
        by   = [c for c in by   if c in df.columns]
        cols = [c for c in cols if c in df.columns]
        if not by:
            return pd.DataFrame(columns=cols)
        return df.groupby(by, as_index=False)[cols].sum()

    return {
        "raw":               sales,                                         # full cleaned df
        "rep_value":         grp(sales, ["Rep Code"],        val_cols),
        "manager_value":     grp(sales, ["Manager Code"],    val_cols),
        "area_value":        grp(sales, ["Area Code"],        val_cols),
        "supervisor_value":  grp(sales, ["Supervisor Code"], val_cols),
        "rep_products":      grp(sales, ["Rep Code",        "Product Code", "Product Name"], prod_cols),
        "manager_products":  grp(sales, ["Manager Code",    "Product Code", "Product Name"], prod_cols),
        "area_products":     grp(sales, ["Area Code",        "Product Code", "Product Name"], prod_cols),
        "supervisor_products":grp(sales, ["Supervisor Code","Product Code", "Product Name"], prod_cols),
    }


# =========================
# 🎯 2 — TARGET PIPELINE
# =========================
def build_target_pipeline(df: pd.DataFrame,
                           id_name: str,
                           mapping: pd.DataFrame) -> dict:

    df      = df.copy()
    mapping = mapping.copy()
    df.columns = df.columns.str.strip()

    # ── 2a. melt wide → long ──────────────────
    fixed  = [c for c in ["Year", "Product Code", "Old Product Name", "Sales Price"] if c in df.columns]
    dynamic= [c for c in df.columns if c not in fixed]

    df = df.melt(id_vars=fixed, value_vars=dynamic,
                 var_name=id_name, value_name="Target (Unit)")

    # ── 2b. clean IDs ─────────────────────────
    df[id_name]       = _clean_id(df[id_name])
    df["Product Code"]= _to_num(df["Product Code"], "Int64")

    mapping["Product Code"] = _to_num(mapping["Product Code"], "Int64")
    mapping_clean = mapping.drop_duplicates("Product Code")

    df = df.merge(mapping_clean, on="Product Code", how="left")

    # ── 2c. numeric ───────────────────────────
    df["Target (Unit)"] = _to_num(df["Target (Unit)"]).fillna(0)
    df["Sales Price"]   = _to_num(df["Sales Price"]).fillna(0)
    df["Full Value"]    = df["Target (Unit)"] * df["Sales Price"]

    # ── 2d. time-weighted slices ──────────────
    month_w   = current_month  / 12
    quarter_w = past_quarters  / 4

    def _slice(weight):
        d = df.copy()
        d["Value"] = d["Full Value"] * weight
        return d

    full    = _slice(1)
    month   = _slice(month_w)
    quarter = _slice(quarter_w)
    ytd     = _slice(month_w)       # YTD = same as month weight here

    # ── 2e. value summary ─────────────────────
    def grp_val(d):
        return d.groupby(id_name, as_index=False)["Value"].sum()

    value_table = grp_val(full).rename(columns={"Value": "Full Year"})
    value_table["Month"]   = grp_val(month)["Value"].values
    value_table["Quarter"] = grp_val(quarter)["Value"].values
    value_table["YTD"]     = grp_val(ytd)["Value"].values

    # ── 2f. product detail per slice ─────────
    def grp_prod(d):
        return d.groupby(
            [id_name, "Product Code", "Product Name"], as_index=False
        ).agg(Units=("Target (Unit)", "sum"), Value=("Value", "sum"))

    return {
        "value_table":      value_table,
        "products_full":    grp_prod(full),
        "products_month":   grp_prod(month),
        "products_quarter": grp_prod(quarter),
        "products_ytd":     grp_prod(ytd),
    }


# =========================
# 📬 3 — OVERDUE PIPELINE
# =========================
def build_overdue_pipeline(overdue: pd.DataFrame,
                            codes: pd.DataFrame) -> dict:

    overdue = overdue.iloc[:, :9].copy()
    overdue.columns = [
        "Client Name", "Client Code",
        "15 Days", "30 Days", "60 Days", "90 Days",
        "120 Days", "More Than 120 Days", "Balance",
    ]

    # ── numeric ───────────────────────────────
    num_cols = ["15 Days","30 Days","60 Days","90 Days",
                "120 Days","More Than 120 Days","Balance"]
    for col in num_cols:
        overdue[col] = _to_num(overdue[col]).fillna(0)

    overdue["Overdue"] = overdue["120 Days"] + overdue["More Than 120 Days"]

    # ── extract rep code from header rows ─────
    overdue["Rep Code"] = pd.NA
    mask = overdue["Client Name"].astype(str).str.strip().eq("كود المندوب")
    overdue.loc[mask, "Rep Code"] = overdue.loc[mask, "Client Code"]
    overdue["Rep Code"] = overdue["Rep Code"].ffill()

    # ── drop non-data rows ────────────────────
    drop_kw = r"اجمالــــــي التقرير|اجمالى الفرع/المندوب|كود الفرع|كود المندوب|اسم العميل"
    overdue = overdue[
        overdue["Client Name"].notna() &
        (overdue["Client Name"].astype(str).str.strip() != "") &
        (~overdue["Client Name"].astype(str).str.contains(drop_kw, na=False))
    ].copy().reset_index(drop=True)

    # ── merge hierarchy ───────────────────────
    codes["Rep Code"]   = _to_num(codes["Rep Code"], "Int64")
    overdue["Rep Code"] = _to_num(overdue["Rep Code"], "Int64")
    overdue = overdue.merge(codes, on="Rep Code", how="left")

    # ── grouped outputs ───────────────────────
    def _summary(df, level):
        return df.groupby(level, as_index=False)["Overdue"].sum()

    def _details(df, level):
        cols = [c for c in [level, "Client Code", "Client Name", "Overdue"] if c in df.columns]
        return df[cols].copy()

    return {
        "raw":                overdue,
        "rep_summary":        _summary(overdue, "Rep Code"),
        "manager_summary":    _summary(overdue, "Manager Code"),
        "area_summary":       _summary(overdue, "Area Code"),
        "supervisor_summary": _summary(overdue, "Supervisor Code"),
        "rep_details":        _details(overdue, "Rep Code"),
        "manager_details":    _details(overdue, "Manager Code"),
        "area_details":       _details(overdue, "Area Code"),
        "supervisor_details": _details(overdue, "Supervisor Code"),
    }


# =========================
# 🗂️ 4 — OPENING PIPELINE
# =========================
def build_opening_pipeline(opening: pd.DataFrame,
                            codes: pd.DataFrame) -> dict:

    opening = opening.copy()
    opening.columns = [
        "Branch", "Evak", "Opening Balance",
        "Total Sales After Invoice Discounts", "Returns",
        "Sales Value Before Extra Discounts",
        "Cash Collection", "Collection Checks",
        "Returned Chick", "Collection Returned Chick",
        "Extra Discounts", "Daienah", "End Balance",
    ]

    # ── extract rep from header rows ──────────
    opening["Rep Code"]    = pd.NA
    opening["Old Rep Name"]= pd.NA
    mask = opening["Branch"].astype(str).str.strip().eq("كود المندوب")
    opening.loc[mask, "Rep Code"]     = opening.loc[mask, "Opening Balance"]
    opening.loc[mask, "Old Rep Name"] = opening.loc[mask, "Total Sales After Invoice Discounts"]
    opening[["Rep Code", "Old Rep Name"]] = opening[["Rep Code", "Old Rep Name"]].ffill()

    # ── drop summary rows ────────────────────
    drop_kw = r"نسبة المندوب|كود المندوب|اجماليات|كود الفرع"
    opening = opening[
        opening["Branch"].notna() &
        (opening["Branch"].astype(str).str.strip() != "") &
        (~opening["Branch"].astype(str).str.contains(drop_kw, na=False))
    ].copy().reset_index(drop=True)

    # ── numeric ───────────────────────────────
    num_cols = [
        "Opening Balance", "Total Sales After Invoice Discounts", "Returns",
        "Sales Value Before Extra Discounts", "Cash Collection",
        "Collection Checks", "Returned Chick", "Collection Returned Chick",
        "Extra Discounts", "Daienah", "End Balance",
    ]
    for col in num_cols:
        opening[col] = _to_num(opening[col]).fillna(0)

    # ── computed KPIs ─────────────────────────
    opening["Total Collection"]   = opening["Cash Collection"] + opening["Collection Checks"]
    opening["Sales After Returns"]= (
        opening["Total Sales After Invoice Discounts"] - opening["Returns"]
    )

    # ── merge hierarchy ───────────────────────
    opening["Rep Code"] = _to_num(opening["Rep Code"], "Int64")
    codes["Rep Code"]   = _to_num(codes["Rep Code"], "Int64")
    opening = opening.merge(codes, on="Rep Code", how="left")

    # ── grouped outputs ───────────────────────
    agg_cols = [
        "Opening Balance", "Cash Collection", "Collection Checks",
        "Total Collection", "Extra Discounts", "End Balance",
        "Sales After Returns",
    ]

    def grp(df, level):
        cols = [c for c in agg_cols if c in df.columns]
        return df.groupby(level, as_index=False)[cols].sum()

    return {
        "raw":                opening,
        "rep_summary":        grp(opening, "Rep Code"),
        "manager_summary":    grp(opening, "Manager Code"),
        "area_summary":       grp(opening, "Area Code"),
        "supervisor_summary": grp(opening, "Supervisor Code"),
    }


# =========================
# 🏆 5 — ACHIEVEMENT
# =========================
def build_achievement(sales_result: dict,
                       target_result: dict,
                       id_name: str) -> pd.DataFrame:
    """
    Merge actual sales value vs target value and compute Achievement %.
    Works for any hierarchy level (Rep / Manager / Area / Supervisor / Evak).

    sales_result  : output of build_sales_pipeline()
    target_result : output of build_target_pipeline()
    id_name       : e.g. "Rep Code", "Manager Code", …
    """
    # pick the right actual table
    level_key = id_name.lower().replace(" ", "_")  # e.g. "rep_code"
    actual_key = level_key.replace("_code", "_value")  # e.g. "rep_value"

    actual = sales_result.get(actual_key, pd.DataFrame())
    target = target_result["value_table"]

    if actual.empty or id_name not in actual.columns:
        return pd.DataFrame()

    # total actual sales value
    actual = actual[[id_name, "Sales After Returns"]].copy()
    actual = actual.rename(columns={"Sales After Returns": "Actual Value"})

    # merge with target slices
    merged = actual.merge(
        target[[id_name, "Full Year", "Month", "Quarter", "YTD"]],
        on=id_name,
        how="outer"
    ).fillna(0)

    def pct(num, den):
        return np.where(den == 0, np.nan, (num / den * 100).round(1))

    merged["Ach% Full Year"] = pct(merged["Actual Value"], merged["Full Year"])
    merged["Ach% Month"]     = pct(merged["Actual Value"], merged["Month"])
    merged["Ach% Quarter"]   = pct(merged["Actual Value"], merged["Quarter"])
    merged["Ach% YTD"]       = pct(merged["Actual Value"], merged["YTD"])

    return merged


# =========================
# 🚀 MASTER BUILD
# =========================
def build_all(data: dict) -> dict:
    """
    Run every pipeline and return a single master dict.
    This is what the Streamlit app should call.
    """
    mapping = data["mapping"]
    codes   = data["codes"]

    # ── sales ─────────────────────────────────
    sales = build_sales_pipeline(data["sales"], mapping, codes)

    # ── targets ───────────────────────────────
    targets = {
        "rep":        build_target_pipeline(data["target_rep"],        "Rep Code",        mapping),
        "manager":    build_target_pipeline(data["target_manager"],    "Manager Code",    mapping),
        "area":       build_target_pipeline(data["target_area"],       "Area Code",       mapping),
        "supervisor": build_target_pipeline(data["target_supervisor"], "Supervisor Code", mapping),
        "evak":       build_target_pipeline(data["target_evak"],       "Evak Code",       mapping),
    }

    # ── overdue ───────────────────────────────
    overdue = build_overdue_pipeline(data["overdue"], codes)

    # ── opening ───────────────────────────────
    opening = build_opening_pipeline(data["opening"], codes)

    # ── achievement ───────────────────────────
    achievement = {
        level: build_achievement(sales, targets[level], f"{level.capitalize()} Code")
        for level in ["rep", "manager", "area", "supervisor"]
    }
    # fix key names (Rep Code → rep, etc.)
    id_map = {
        "rep": "Rep Code", "manager": "Manager Code",
        "area": "Area Code", "supervisor": "Supervisor Code",
    }
    achievement = {
        level: build_achievement(sales, targets[level], id_map[level])
        for level in id_map
    }

    return {
        "sales":       sales,
        "targets":     targets,
        "overdue":     overdue,
        "opening":     opening,
        "achievement": achievement,
    }
