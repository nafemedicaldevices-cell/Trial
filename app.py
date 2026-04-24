import pandas as pd
import numpy as np
import os

def load_client_haraka():

    file_path = "Client Harakah.xlsx"

    # =========================
    # 📂 SAFE FILE CHECK
    # =========================
    if not os.path.exists(file_path):
        return pd.DataFrame({"Error": [f"File not found: {file_path}"]})

    # =========================
    # 📥 LOAD
    # =========================
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        return pd.DataFrame({"Error": [str(e)]})

    # =========================
    # 🧹 BASIC CLEAN
    # =========================
    if df.empty:
        return pd.DataFrame({"Error": ["Empty Excel file"]})

    first_col = df.columns[0]
    df[first_col] = df[first_col].astype(str)

    df = df[
        df[first_col].notna() &
        (df[first_col].str.strip() != "") &
        (~df[first_col].str.contains("كود الفرع", na=False)) &
        (~df[first_col].str.contains("كود العميل", na=False))
    ].copy()

    df = df.reset_index(drop=True)

    # =========================
    # 🧾 SAFE RENAME (NO CRASH)
    # =========================
    expected_cols = [
        "Client Code",
        "Client Name",
        "Opening Balance",
        "Sales Value",
        "Returns Value",
        "Tasweyat Madinah (Credit)",
        "Total Collection",
        "Madfoaat",
        "Tasweyat Madinah (Debit)",
        "End Balance",
        "Motalbet El Fatrah"
    ]

    col_count = min(len(expected_cols), df.shape[1])
    df = df.iloc[:, :col_count]
    df.columns = expected_cols[:col_count]

    # =========================
    # 🧠 REP EXTRACTION (SAFE)
    # =========================
    if "Sales Value" in df.columns:

        marker = df["Sales Value"].astype(str).str.contains("مندوب المبيعات", na=False)

        if "Returns Value" in df.columns:
            df["Rep Code"] = np.where(marker, df["Returns Value"], np.nan)

        if "Tasweyat Madinah (Credit)" in df.columns:
            df["Rep Name"] = np.where(marker, df["Tasweyat Madinah (Credit)"], np.nan)

        df["Rep Code"] = df["Rep Code"].ffill() if "Rep Code" in df.columns else None
        df["Rep Name"] = df["Rep Name"].ffill() if "Rep Name" in df.columns else None

    # =========================
    # 🔢 NUMERIC CLEAN
    # =========================
    num_cols = [
        "Opening Balance",
        "Sales Value",
        "Returns Value",
        "Tasweyat Madinah (Credit)",
        "Total Collection",
        "Madfoaat",
        "Tasweyat Madinah (Debit)",
        "End Balance",
        "Motalbet El Fatrah"
    ]

    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return dfس
