import pandas as pd

# =========================
# 🧹 CLEAN FUNCTION
# =========================
def remove_empty_first_column(df):
    first_col = df.columns[0]

    df[first_col] = df[first_col].astype(str).str.strip()

    df = df[
        (df[first_col].notna()) &
        (df[first_col] != "") &
        (df[first_col].str.lower() != "nan")
    ]

    return df


# =========================
# 📥 LOAD TARGETS
# =========================
def load_targets():
    df = pd.read_excel("Targets.xlsx")
    return df


# =========================
# 📥 LOAD REP HARKA
# =========================
def load_haraka():
    df = pd.read_excel("Rep Haraka.xlsx")

    # 🔥 أهم سطر
    df = remove_empty_first_column(df)

    return df


# =========================
# 📥 LOAD CLIENT HARKA
# =========================
def load_client_haraka():
    df = pd.read_excel("Client Haraka.xlsx")

    # 🔥 أهم سطر
    df = remove_empty_first_column(df)

    return df
