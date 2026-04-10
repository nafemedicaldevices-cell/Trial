import pandas as pd

# =========================
# 📥 LOAD DATA
# =========================
def load_data(path="Overdue.xlsx"):
    df = pd.read_excel(path)
    return df


# =========================
# 🧼 CLEAN DATA
# =========================
def clean_data(df):
    df = df.copy()

    # 1️⃣ تنظيف أسماء الأعمدة
    df.columns = df.columns.str.strip()

    # 2️⃣ حذف الصفوف الفاضية بالكامل
    df = df.dropna(how="all")

    # 3️⃣ حذف التكرارات
    df = df.drop_duplicates()

    # 4️⃣ تنظيف النصوص
    obj_cols = df.select_dtypes(include="object").columns
    for col in obj_cols:
        df[col] = df[col].astype(str).str.strip()

    # 5️⃣ توحيد القيم الفاضية
    df = df.replace(["", "NA", "N/A", "null", "None"], pd.NA)

    return df
