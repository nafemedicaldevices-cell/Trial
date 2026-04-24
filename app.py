import pandas as pd
import numpy as np
import os

def load_client_haraka():

    # =========================
    # 📂 CHECK FILE
    # =========================
    file_path = "Client Harakah.xlsx"

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"❌ File not found: {file_path}")

    # =========================
    # 📥 LOAD FILE
    # =========================
    df = pd.read_excel(file_path)

    # =========================
    # 🧹 CLEAN FIRST COLUMN
    # =========================
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
    # 🧾 SAFE COLUMN RENAME
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

    df = df.iloc[:, :len(expected_cols)]
    df.columns = expected_cols[:df.shape[1]]

    # =========================
    # 🧠 EXTRACT REP INFO
    # =========================
    marker = df["Sales Value"].astype(str).str.contains("مندوب المبيعات", na=False)

    df["Rep Code"] = np.where(marker, df["Returns Value"], np.nan)
    df["Rep Name"] = np.where(marker, df["Tasweyat Madinah (Credit)"], np.nan)

    df["Rep Code"] = df["Rep Code"].ffill()
    df["Rep Name"] = df["Rep Name"].ffill()

    # =========================
    # 🔢 NUMERIC CONVERSION
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

    return df
