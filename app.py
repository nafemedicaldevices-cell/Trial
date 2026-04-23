import pandas as pd
import numpy as np

# =========================
# 📂 FILES (ALL SHEETS)
# =========================
files = {
    "Rep": "Target Rep.xlsx",
    "Manager": "Target Manager.xlsx",
    "Area": "Target Area.xlsx",
    "Supervisor": "Target Supervisor.xlsx",
    "Evak": "Target Evak.xlsx",
}

all_data = []

# =========================
# 🔄 PROCESS EACH FILE
# =========================
for level, file in files.items():

    df = pd.read_excel(file)
    df.columns = df.columns.str.strip()

    # =========================
    # 📌 FIXED COLUMNS
    # =========================
    fixed_cols = [
        "Year",
        "Product Code",
        "Old Product Name",
        "Sales Price"
    ]

    # =========================
    # 🔄 UNPIVOT (WIDE → LONG)
    # =========================
    df = df.melt(
        id_vars=fixed_cols,
        var_name="Code",
        value_name="Target (Year)"
    )

    df["Level"] = level

    # =========================
    # 🧹 CLEAN
    # =========================
    df["Target (Year)"] = pd.to_numeric(df["Target (Year)"], errors="coerce")

    # =========================
    # 📅 CALC
    # =========================
    df["Target (Unit)"] = df["Target (Year)"] / 12
    df["Target (Value)"] = df["Target (Unit)"] * df["Sales Price"]

    # =========================
    # 📅 MONTH EXPANSION
    # =========================
    months = [
        "Jan","Feb","Mar","Apr","May","Jun",
        "Jul","Aug","Sep","Oct","Nov","Dec"
    ]

    df_long = df.loc[df.index.repeat(12)].copy()

    df_long["Month"] = np.tile(months, len(df))

    df_long["Monthly Target (Unit)"] = np.repeat(df["Target (Unit)"].values, 12)

    df_long["Monthly Target (Value)"] = np.repeat(df["Target (Value)"].values, 12) / 12

    all_data.append(df_long)

# =========================
# 📊 COMBINE ALL SHEETS
# =========================
final_df = pd.concat(all_data, ignore_index=True)

# =========================
# 💾 SAVE NEW FILE
# =========================
output_file = "Clean_Target_Output.xlsx"
final_df.to_excel(output_file, index=False)

print("Done ✅ File saved:", output_file)
