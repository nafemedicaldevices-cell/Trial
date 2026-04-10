
import pandas as pd
import numpy as np


def safe_group(df, group_cols, sum_cols):
    group_cols = [c for c in group_cols if c in df.columns]
    sum_cols = [c for c in sum_cols if c in df.columns]

    if not group_cols:
        return pd.DataFrame()

    return df.groupby(group_cols, as_index=False)[sum_cols].sum()


def build_overdue_pipeline(overdue, codes):

    df = overdue.copy()
    df.columns = df.columns.str.strip()

    # =========================
    # 📌 BASIC CLEANING
    # =========================
    df = df.iloc[:, :9]
    df.columns = [
        "Client Name", "Client Code", "15 Days", "30 Days", "60 Days",
        "90 Days", "120 Days", "More Than 120 Days", "Balance"
    ]

    # =========================
    # 🧩 INIT FIELDS
    # =========================
    df["Rep Code"] = None
    df["Old Rep Name"] = None

    # =========================
    # 🔎 EXTRACT REP HEADER
    # =========================
    mask = df["Client Name"].astype(str).str.strip().eq("كود المندوب")

    df.loc[mask, "Rep Code"] = df.loc[mask, "Client Code"]
    df.loc[mask, "Old Rep Name"] = df.loc[mask, "30 Days"]

    df[["Rep Code", "Old Rep Name"]] = df[
        ["Rep Code", "Old Rep Name"]
    ].ffill()

    # =========================
    # 🧹 FILTER
    # =========================
    drop_keywords = "اجمالى|تقرير|كود الفرع|كود المندوب|اسم العميل"

    df = df[
        df["Client Name"].notna() &
        (df["Client Name"].astype(str).str.strip() != "") &
        (~df["Client Name"].astype(str).str.contains(drop_keywords, na=False))
    ].copy()

    # =========================
    # 🔢 NUMERIC
    # =========================
    num_cols = [
        "15 Days", "30 Days", "60 Days", "90 Days",
        "120 Days", "More Than 120 Days",
        "Client Code", "Rep Code"
    ]

    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["Rep Code"] = pd.to_numeric(df["Rep Code"], errors="coerce")
    df["Client Code"] = pd.to_numeric(df["Client Code"], errors="coerce")

    # =========================
    # 💰 KPI
    # =========================
    df["Overdue"] = df["120 Days"] + df["More Than 120 Days"]

    # =========================
    # 🔗 MERGE
    # =========================
    codes = codes.copy()
    codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")

    df = df.merge(codes, on="Rep Code", how="left")

    # =========================
    # 📦 GROUPS
    # =========================
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
        results[name] = safe_group(df, g, s)

    return results
