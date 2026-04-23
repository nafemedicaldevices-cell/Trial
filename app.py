def add_columns(data):

    # =========================
    # SALES FIX
    # =========================
    df = data["sales"].copy()

    # 🔹 تحويل أرقام بالقوة (أهم سطر)
    df["Sales Unit Before Edit"] = pd.to_numeric(df["Sales Unit Before Edit"], errors="coerce").fillna(0)
    df["Returns Unit Before Edit"] = pd.to_numeric(df["Returns Unit Before Edit"], errors="coerce").fillna(0)
    df["Sales Price"] = pd.to_numeric(df["Sales Price"], errors="coerce").fillna(0)

    # 🔹 الحسابات
    df["Total Sales Value"] = df["Sales Unit Before Edit"] * df["Sales Price"]
    df["Returns Value"] = df["Returns Unit Before Edit"] * df["Sales Price"]
    df["Net Sales Value"] = df["Total Sales Value"] - df["Returns Value"]

    data["sales"] = df

    # =========================
    # OPENING
    # =========================
    df = data["opening"]

    df["Total Sales"] = pd.to_numeric(df["Total Sales"], errors="coerce").fillna(0)
    df["Returns"] = pd.to_numeric(df["Returns"], errors="coerce").fillna(0)
    df["Cash Collection"] = pd.to_numeric(df["Cash Collection"], errors="coerce").fillna(0)
    df["Collection Checks"] = pd.to_numeric(df["Collection Checks"], errors="coerce").fillna(0)

    df["Total Collection"] = df["Cash Collection"] + df["Collection Checks"]
    df["Sales After Returns"] = df["Total Sales"] - df["Returns"]

    data["opening"] = df

    # =========================
    # OVERDUE
    # =========================
    df = data["overdue"]

    num_cols = ["30 Days","60 Days","90 Days","120 Days","150 Days","More Than 150 Days"]

    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["Overdue Value"] = df[["120 Days","150 Days","More Than 150 Days"]].sum(axis=1)
    df["Total Balance"] = df[num_cols].sum(axis=1)

    data["overdue"] = df

    return data
