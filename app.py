import streamlit as st
import data_pipeline as dp

st.title("Sales Dashboard")

# مثال تشغيل
data = dp.load_data()   # لو عندك load_data جوه pipeline
st.write(data["sales"].head())
