import pandas as pd

# =========================
# 📂 LOAD DATA
# =========================
df = pd.read_excel("Target Rep.xlsx")

# =========================
# 📌 FIXED COLUMNS
# =========================
fixed_cols = ["Year", "Product Code", "Old Product Name", "Sales Price"]

# =========================
# 🧠 DETECT LEVEL COLUMNS (غير الثابتة)
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
# 🏷️ تحديد نوع الكود (Rep / Area / Supervisor...)
# =========================
def detect_level(code):
    # لو عندك naming convention عدليه هنا
    if "Rep" in code:
        return "Rep"
    elif "Area" in code:
        return "Area"
    elif "Supervisor" in code:
        return "Supervisor"
    elif "Manager" in code:
        return "Manager"
    else:
        return "Company"

df_melted["Level"] = df_melted["Code"].apply(detect_level)

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
    ["Year", "Product Code", "Old Product Name", "Sales Price",
     "Level", "Code", "Target (Year)", "Target (Unit)", "Target (Value)"]
]

# =========================
# 💾 SAVE
# =========================
df_final.to_excel("Target_Clean_Output.xlsx", index=False)

print("Done ✅")
