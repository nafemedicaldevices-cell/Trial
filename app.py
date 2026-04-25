import pandas as pd

st.write("📂 Trying to load Sales file...")

try:
    df = pd.read_excel("Sales.xlsx")
    st.write("✅ File loaded successfully")
    st.write("📊 Columns:", df.columns.tolist())
    st.dataframe(df.head())
except Exception as e:
    st.error("❌ Error loading file")
    st.exception(e)
