import streamlit as st
import data_pipeline as dp

st.title("Sales Target Dashboard")

# =========================
# LOAD DATA
# =========================
data = dp.load_data()

# =========================
# BUILD ALL LEVELS
# =========================
rep = dp.build_target_pipeline(data["target_rep"], "Rep Code", data["mapping"])
manager = dp.build_target_pipeline(data["target_manager"], "Manager Code", data["mapping"])
area = dp.build_target_pipeline(data["target_area"], "Area Code", data["mapping"])
supervisor = dp.build_target_pipeline(data["target_supervisor"], "Supervisor Code", data["mapping"])
evak = dp.build_target_pipeline(data["target_evak"], "Evak Code", data["mapping"])

# =========================
# SELECT LEVEL
# =========================
level = st.selectbox(
    "Choose Level",
    ["Rep", "Manager", "Area", "Supervisor", "Evak"]
)

data_map = {
    "Rep": rep,
    "Manager": manager,
    "Area": area,
    "Supervisor": supervisor,
    "Evak": evak
}

selected = data_map[level]

# =========================
# KPI TABLES
# =========================
st.subheader(f"{level} Target Values")

st.write("Full Year")
st.dataframe(selected["value_full"])

st.write("Month")
st.dataframe(selected["value_month"])

st.write("Quarter (Dynamic)")
st.dataframe(selected["value_quarter"])

st.write("Up To Date (YTD)")
st.dataframe(selected["value_uptodate"])

# =========================
# PRODUCTS
# =========================
st.subheader(f"{level} Products")

st.write("Full")
st.dataframe(selected["products_full"])

st.write("Month")
st.dataframe(selected["products_month"])

st.write("Quarter")
st.dataframe(selected["products_quarter"])

st.write("Up To Date")
st.dataframe(selected["products_uptodate"])

    # CLEAN
    df.columns = df.columns.str.strip()

    fixed_cols = [c for c in ["Year", "Product Code", "Old Product Name", "Sales Price"] if c in df.columns]
    dynamic_cols = [c for c in df.columns if c not in fixed_cols]

    # MELT
    df = df.melt(
        id_vars=fixed_cols,
        value_vars=dynamic_cols,
        var_name=id_name,
        value_name="Target (Unit)"
    )

    # CLEAN IDS
    df[id_name] = pd.to_numeric(
        df[id_name].astype(str).str.replace(r"[^0-9]", "", regex=True),
        errors="coerce"
    )

    # NUMERIC
    df["Product Code"] = pd.to_numeric(df["Product Code"], errors="coerce")
    df["Target (Unit)"] = pd.to_numeric(df["Target (Unit)"], errors="coerce").fillna(0)
    df["Sales Price"] = pd.to_numeric(df["Sales Price"], errors="coerce").fillna(0)

    # MAPPING
    mapping["Product Code"] = pd.to_numeric(mapping["Product Code"], errors="coerce")
    mapping = mapping.drop_duplicates("Product Code")

    df = df.merge(
        mapping[["Product Code", "Product Name", "Category", "2 Classification"]],
        on="Product Code",
        how="left"
    )

    # BASE VALUE
    df["Full Target Value"] = df["Target (Unit)"] * df["Sales Price"]

    # KPI CALCULATION
    def add(df_in, factor):
        tmp = df_in.copy()
        tmp["Target (Value)"] = (tmp["Full Target Value"] / 12) * factor
        return tmp

    df_full = add(df, 12)
    df_month = add(df, 1)
    df_quarter = add(df, 3)
    df_ytd = add(df, current_month)

    # GROUP VALUE
    def value(d):
        return d.groupby([id_name], as_index=False)["Target (Value)"].sum()

    # GROUP PRODUCTS
    def products(d):
        return d.groupby(
            [id_name, "Product Code", "Product Name"],
            as_index=False
        )["Target (Value)"].sum()

    return {
        # RAW
        "full": df,

        # VALUES
        "value_full": value(df_full),
        "value_month": value(df_month),
        "value_quarter": value(df_quarter),
        "value_uptodate": value(df_ytd),

        # PRODUCTS
        "products_full": products(df_full),
        "products_month": products(df_month),
        "products_quarter": products(df_quarter),
        "products_uptodate": products(df_ytd),
    }
