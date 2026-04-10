import streamlit as st
import pandas as pd

st.title("📊 Sales Dashboard")

sales = pd.read_excel("Sales.xlsx")
overdue = pd.read_excel("Overdue.xlsx")
opening = pd.read_excel("Opening.xlsx")

st.success("Data loaded successfully ✅")

st.write(sales.head())
