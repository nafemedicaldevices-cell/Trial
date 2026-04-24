# =========================
# 🧠 CLEAN COLUMN NAMES
# =========================
codes.columns = codes.columns.str.strip()
df.columns = df.columns.str.strip()

# =========================
# 🔢 FORCE SAME TYPE
# =========================
df["Rep Code"] = pd.to_numeric(df["Rep Code"], errors="coerce")
codes["Rep Code"] = pd.to_numeric(codes["Rep Code"], errors="coerce")

# =========================
# 🧹 DROP DUPLICATES IN CODES
# =========================
codes = codes.drop_duplicates(subset=["Rep Code"])

# =========================
# 🔍 DEBUG CHECK (IMPORTANT)
# =========================
st.write("DF Rep Codes sample:", df["Rep Code"].dropna().unique()[:10])
st.write("Codes Rep Codes sample:", codes["Rep Code"].dropna().unique()[:10])

# =========================
# 🔗 SAFE MERGE
# =========================
df = df.merge(codes, on="Rep Code", how="left")

# =========================
# 🔍 CHECK RESULT
# =========================
st.write("Matched rows:", df[codes.columns].notna().any(axis=1).sum())
