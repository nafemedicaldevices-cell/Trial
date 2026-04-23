import pandas as pd

# =========================
# 📂 LOAD ALL SHEETS
# =========================
file = pd.ExcelFile("Target Rep.xlsx")

df_list = []

for sheet in file.sheet_names:
    df = pd.read_excel(file, sheet_name=sheet)
    df["Source Sheet"] = sheet   # تحديد المستوى من اسم الشيت
    df_list.append(df)

# دمج كل الشيتات
df = pd.concat(df_list, ignore_index=True)

# =========================
# 📌 FIXED COLUMNS
# =========================
fixed_cols = ["Year", "Product Code", "Old Product Name", "Sales Price", "Source Sheet"]

# =========================
# 🧠 DETECT LEVEL COLUMNS
# =========================
level_cols = [col for col in df.columns if col not in fixed_cols]

# =========================
# 🔄 UNPIVOT
# =========================
df_melted = df.melt(
    id_vars=fixed_cols,
    value_vars=level_cols,
    var_name="Code",
    value_name="Target (Year)"
)

# =========================
# 🏷️ LEVEL FROM SHEET NAME (أفضل من parsing)
# =========================
df_melted["Level"] = df_melted["Source Sheet"]

# =========================
# 🧮 CLEAN + CALCULATIONS
# =========================
df_melted["Target (Year)"] = pd.to_numeric(df_melted["Target (Year)"], errors="coerce")

df_melted["Target (Unit)"] = df_melted["Target (Year)"] / 12
df_melted["Target (Value)"] = df_melted["Target (Unit)"] * df_melted["Sales Price"]

# =========================
# 🧹 FINAL STRUCTURE
# =========================
df_final = df_melted[
    [
        "Year",
        "Product Code",
        "Old Product Name",
        "Sales Price",
        "Level",
        "Code",
        "Target (Year)",
        "Target (Unit)",
        "Target (Value)"
    ]
]

# =========================
# 💾 SAVE OUTPUT
# =========================
df_final.to_excel("Target_Clean_Output.xlsx", index=False)

print("Done ✅ File Created: Target_Clean_Output.xlsx")
