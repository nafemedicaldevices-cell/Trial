import pandas as pd
import numpy as np


def build_overdue_pipeline(overdue, codes):

    overdue = overdue.copy()
    overdue.columns = overdue.columns.str.strip()

    # =========================
    # 📌 CLEANING
    # =========================
    overdue = overdue.iloc[:, :9]
    overdue.columns = [
        "Client Name", "Client Code", "15 Days", "30 Days", "60 Days",
        "90 Days", "120 Days", "More Than 120 Days", "Balance"
    ]

    # =========================
    # 🧩 INIT REP FIELDS
    # =========================
    overdue["Rep Code"] = np.nan
    overdue["Old Rep Name"] = np.nan

    overdue["Rep Code"] = overdue["Rep Code"].astype("object")
    overdue["Old Rep Name"] = overdue["Old Rep Name"].astype("object")

    # =========================
    # 🔎 EXTRACT REP HEADER
    # =========================
    mask = overdue["Client Name"].astype(str).str.strip().eq("كود المندوب")

    overdue.loc[mask, "Rep Code"] = overdue.loc[mask, "Client Code"].astype(str)
    overdue.loc[mask, "Old Rep Name"] = overdue.loc[mask, "30 Days"].astype(str)

    overdue[["Rep Code", "Old Rep Name"]] = overdue[
        ["Rep Code", "Old Rep Name"]
    ].ffill()

    # =========================
    # 🧹 FILTER
    # =========================
    drop_keywords = "اجمالــــــي التقرير|اجمالى الفرع/المندوب|كود الفرع|كود المندوب|اسم العميل"

    overdue = overdue[
        overdue["Client Name"].notna() &
        (overdue["Client Name"].astype(str).str.strip() != "") &
        (~overdue["Client Name"].astype(str).str.contains(drop_keywords, na=False))
    ].copy()

    # =========================
    # 🔢 NUMERIC
    # =========================
    num_cols = [
        "15 Days", "30 Days", "60 Days", "90 Days",
        "120 Days", "More Than 120 Days",
        "Client Code"
    ]

    for col in num_cols:
        if col in overdue.columns:
            overdue[col] = pd.to_numeric(overdue[col], errors="coerce").fillna(0)

    overdue["Rep Code"] = pd.to_numeric(overdue["Rep Code"], errors="coerce")

    # =========================
    # 💰 KPI
    # =========================
    overdue["Overdue"] = overdue["120 Days"] + overdue["More Than 120 Days"]

    # =========================
    # 🔗 MERGE CODES
    # =========================
    codes = codes.copy()
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")

    overdue = overdue.merge(codes, on="Rep Code", how="left")

    # =========================
    # 📊 GROUP ENGINE
    # =========================
    def safe_group(df, group_cols, sum_cols):
        group_cols = [c for c in group_cols if c in df.columns]
        sum_cols = [c for c in sum_cols if c in df.columns]

        if not group_cols:
            return pd.DataFrame()

        return df.groupby(group_cols, as_index=False)[sum_cols].sum()

    GROUPS = {
        "rep_value": (["Rep Code"], ["Overdue"]),
        "manager_value": (["Manager Code"], ["Overdue"]),
        "area_value": (["Area Code"], ["Overdue"]),
        "supervisor_value": (["Supervisor Code"], ["Overdue"]),

        "rep_client": (["Rep Code", "Client Code"], ["Overdue"]),
        "manager_client": (["Manager Code", "Client Code"], ["Overdue"]),
        "area_client": (["Area Code", "Client Code"], ["Overdue"]),
        "supervisor_client": (["Supervisor Code", "Client Code"], ["Overdue"]),
    }

    results = {}

    for name, (g, s) in GROUPS.items():
        results[name] = safe_group(overdue, g, s)

    return results
