import pandas as pd

def load_data():

    df = pd.read_excel("Rep Harakah.xlsx")

    # =========================
    # 🧹 CLEAN SPACES
    # =========================
    df = df.replace(r'^\s*$', pd.NA, regex=True)

    first_col = df.columns[0]
    df[first_col] = df[first_col].astype(str)

    # =========================
    # ❌ REMOVE BAD ROWS
    # =========================
    df = df[
        df[first_col].notna() &
        (df[first_col].str.strip() != "") &
        (~df[first_col].str.contains("كود الفرع", na=False)) &
        (~df[first_col].str.contains("كود المندوب", na=False)) &
        (~df[first_col].str.contains("nan", na=False))
    ]

    # =========================
    # 🏷️ FIX DUPLICATE COLUMNS
    # =========================
    cols = df.columns.tolist()
    seen = {}
    new_cols = []

    for c in cols:
        if c in seen:
            seen[c] += 1
            new_cols.append(f"{c}_{seen[c]}")
        else:
            seen[c] = 0
            new_cols.append(c)

    df.columns = new_cols

    # =========================
    # ✏️ RENAME
    # =========================
    df = df.rename(columns={
        df.columns[0]: "Rep Code",
        df.columns[1]: "Rep Name",
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

    return df
