import pandas as pd

# =========================
# 📥 LOAD DATA
# =========================
def load_data(path="Overdue.xlsx"):
    df = pd.read_excel(path)
    return df


# =========================
# 🧼 CLEAN + RENAME COLUMNS
# =========================
def clean_data(df):
    df = df.copy()

    # أول 9 أعمدة فقط
    df = df.iloc[:, :9]

    # إعادة تسمية الأعمدة
    df.columns = [
        "Client Name", "Client Code", "15 Days", "30 Days", "60 Days",
        "90 Days", "120 Days", "More Than 120 Days", "Balance"
    ]

    return df
