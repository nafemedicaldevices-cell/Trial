import streamlit as st
import pandas as pd

# 1️⃣ LOAD DATA FIRST
sales = pd.read_excel("Sales.xlsx")   # أو من linking

# 2️⃣ CLEAN / COPY
sales = sales.copy()

# 3️⃣ FILTERS
...
