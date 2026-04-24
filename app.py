import pandas as pd
import numpy as np

def load_client_haraka():

    # =========================
    # 📥 LOAD FILE
    # =========================
    df = pd.read_excel("Client Harakah.xlsx")

    # =========================
    # 🧹 CLEAN FIRST COLUMN (IMPORTANT)
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
    # 🧾 RENAME COLUMNS
    # =========================
    df = df.rename(columns={
        df.columns[0]: "Client Code",
        df.columns[1]: "Client Name",
        df.columns[2]: "Opening Balance",
        df.columns[3]: "Sales Value",
        df.columns[4]: "Returns Value",
        df.columns[5]: "Tasweyat Madinah (Credit)",
        df.columns[6]: "Total Collection",
        df.columns[7]: "Madfoaat",
        df.columns[8]: "Tasweyat Madinah (Debit)",
        df.columns[9]: "End Balance",
        df.columns[10]: "Motalbet El Fatrah",
    })

    # =========================
    # 🧠 EXTRACT REP INFO
    # (from Sales Value marker row)
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
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # =========================
    # 🔚 RETURN
    # =========================
    return df
