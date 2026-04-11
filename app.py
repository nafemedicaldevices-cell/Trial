# =========================
# REP EXTRACTION
# =========================
opening["Rep Code"] = pd.NA
opening["Old Rep Name"] = pd.NA

mask = opening["Branch"].astype(str).str.strip().eq("كود المندوب")

opening.loc[mask, "Rep Code"] = opening.loc[mask, "Opening Balance"]
opening.loc[mask, "Old Rep Name"] = opening.loc[mask, "Total Sales After Invoice Discounts"]

opening[["Rep Code", "Old Rep Name"]] = opening[["Rep Code", "Old Rep Name"]].ffill()
