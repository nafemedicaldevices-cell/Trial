import pandas as pd
import numpy as np

# =========================
# 📂 LOAD DATA
# =========================
df = pd.read_excel("Target Rep.xlsx")

df.columns = df.columns.str.strip()

# =========================
# 📌 FIXED COLUMNS (NOT TO MELT)
# =========================
fixed_cols = [
    "Year",
    "Product Code",
    "Old Product Name",
    "Sales Price"
]

# =========================
# 🔄 PIVOT → LONG (UNPIVOT)
# =========================
df_long = df.melt(
    id_vars=fixed_cols,
    var_name="Code",
    value_name="Target (Year)"
)

# =========================
# 🧹 CLEAN
# =========================
df_long["Target (Year)"] = pd.to_numeric(df_long["Target (Year)"], errors="coerce")

# =========================
# 📅 CALCULATIONS
# =========================
df_long["Target (Unit)"] = df_long["Target (Year)"] / 12
df_long["Target (Value)"] = df_long["Target (Unit)"] * df_long["Sales Price"]

# =========================
# 📅 MONTH GENERATION
# =========================
months = [
    "Jan","Feb","Mar","Apr","May","Jun",
    "Jul","Aug","Sep","Oct","Nov","Dec"
]

df_final = df_long.loc[df_long.index.repeat(12)].copy()

df_final["Month"] = np.tile(months, len(df_long))

df_final["Monthly Target (Unit)"] = np.repeat(df_long["Target (Unit)"].values, 12)

df_final["Monthly Target (Value"] = np.repeat(df_long["Target (Value)"].values, 12) / 12

# =========================
# 📊 RESULT
# =========================
print(df_final.head())
