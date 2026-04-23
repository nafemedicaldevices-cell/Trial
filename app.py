import pandas as pd
import streamlit as st

st.title("📊 Target Dashboard (Multi Sheets)")

# =========================
# 📂 LOAD EXCEL SHEETS
# =========================
@st.cache_data
def load_data():
    file = pd.ExcelFile("Target Rep.xlsx")

    sheets_data = {}

    for sheet in file.sheet_names:
        df = pd.read_excel(file, sheet_name=sheet)
        df["Level"] = sheet   # اسم الشيت = المستوى
        sheets_data[sheet] = df

    return sheets_data

data = load_data()

# =========================
# 🎛️ SELECT SHEET
# =========================
sheet_choice = st.sidebar.selectbox("Select Level", list(data.keys()))

df = data[sheet_choice]

# =========================
# 📊 SHOW RAW DATA
# =========================
st.subheader(f"📌 Data - {sheet_choice}")
st.dataframe(df, use_container_width=True)

# =========================
# 🧮 BASIC CALCULATIONS (لو عندك Target Year)
# =========================
if "Target" in df.columns or "Total" in df.columns:

    # حاول نلقط العمود الصح تلقائيًا
    target_col = [col for col in df.columns if "target" in col.lower()][0]

    df[target_col] = pd.to_numeric(df[target_col], errors="coerce")

    st.subheader("📊 KPI")

    col1, col2 = st.columns(2)

    col1.metric("Total Target", f"{df[target_col].sum():,.0f}")
    col2.metric("Avg Target", f"{df[target_col].mean():,.0f}")

# =========================
# 💾 DOWNLOAD
# =========================
csv = df.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇️ Download Sheet Data",
    csv,
    f"{sheet_choice}_data.csv",
    "text/csv"
)
