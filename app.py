import pandas as pd
import streamlit as st

st.title("📊 Rep Harakah - Clean & KPI Ready")

# =========================
# 📂 LOAD DATA
# =========================
@st.cache_data
def load_data():
    df = pd.read_excel("Rep Harakah.xlsx")

    # =========================
    # 🧹 REMOVE EMPTY ROWS
    # =========================
    df = df.dropna(how="all")

    # =========================
    # 🧹 CLEAN FIRST COLUMN (Remove unwanted rows)
    # =========================
    first_col = df.columns[0]
    df[first_col] = df[first_col].astype(str)

    df = df[
        ~df[first_col].str.contains("كود الفرع", na=False)
        & ~df[first_col].str.contains("كود المندوب", na=False)
        & (df[first_col].str.strip() != "")
        & (df[first_col] != "nan")
    ]

    # =========================
    # 🏷️ HANDLE DUPLICATE COLUMN NAMES
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
    # ✏️ RENAME COLUMNS CLEAN
    # =========================
    df = df.rename(columns={
        df.columns[0]: "Rep Code",
        df.columns[1]: "Rep Name",
        df.columns[2]: "Opening Balance",
        df.columns[3]: "Sales Value",
        df.columns[4]: "Returns Value",
        df.columns[5]: "Tasweyat Madinah (Credit)",
        df.columns[6]: "Total Collection",
        df.columns[7]: "Tasweyat Dainah",
        df.columns[8]: "Tasweyat Madinah (Debit)",
        df.columns[9]: "End Balance",
        df.columns[10]: "Motalbet El Fatrah",
    })

    return df


# =========================
# 🚀 RUN APP
# =========================
df = load_data()

st.subheader("📌 Clean Data")
st.dataframe(df)

# =========================
# 📊 BASIC KPI
# =========================
st.subheader("📊 Summary")

st.write("Rows:", len(df))
st.write("Columns:", len(df.columns))

st.subheader("📊 Numeric Summary")
st.write(df.describe())
