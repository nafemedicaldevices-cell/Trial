import pandas as pd

def load_client_haraka():

    df = pd.read_excel("Client Harakah.xlsx")

    df = df.replace(r'^\s*$', pd.NA, regex=True)
    df = df.dropna(how="all")

    # =========================
    # 🧹 حذف الصفوف اللي فيها هيدر
    # =========================
    df = df[~df.astype(str).apply(
        lambda x: x.str.contains(
            "رصيد افتتاحى|صافى مبيعات|صافى مرتجع مبيعات|مندوب المبيعات",
            na=False
        )
    ).any(axis=1)]

    # =========================
    # 🏷️ الأعمدة
    # =========================
    df.columns = [
        "Client Code",
        "Client Name",
        "Opening Balance",
        "Sales Value",
        "Returns Value",
        "Tasweyat Madinah",
        "Total Collection",
        "Madfoaat",
        "Tasweyat Dainah",
        "End Balance",
        "Motalbet El Fatrah"
    ]

    # =========================
    # 👤 Rep Name (Fill Down مباشر)
    # =========================
    df["Rep Name"] = df["Tasweyat Madinah"].copy()

    # تحويل "تسويات مدينة" لـ NaN عشان مايتحسبش اسم
    df.loc[df["Rep Name"].astype(str).str.contains("تسويات مدينة", na=False), "Rep Name"] = pd.NA

    # 🔁 Fill Down (ده أهم سطر)
    df["Rep Name"] = df["Rep Name"].ffill()

    return df
