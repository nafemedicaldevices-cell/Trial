import streamlit as st
from cleaning import load_targets, load_haraka, load_client_haraka

st.set_page_config(layout="wide")

# =========================
# 📊 TITLE
# =========================
st.title("📊 KPI + Harakah System")

# =========================
# ⚡ LOAD DATA (CACHED)
# =========================
@st.cache_data
def load_all():
    return load_targets(), load_haraka(), load_client_haraka()

targets, rep_haraka, client_haraka = load_all()

# =========================
# 📌 FILTER
# =========================
level_filter = st.selectbox(
    "Select Level",
    ["All", "Rep", "Manager", "Area", "Supervisor", "Evak"]
)

# =========================
# 📌 TABS
# =========================
tab1, tab2, tab3 = st.tabs([
    "Targets",
    "Rep Harakah",
    "Client Harakah"
])

# =========================
# 📊 TARGETS
# =========================
with tab1:

    if level_filter == "All":
        df_show = targets
    else:
        df_show = targets[targets["Level"] == level_filter]

    st.dataframe(df_show, use_container_width=True)


# =========================
# 📊 REP HARKA
# =========================
with tab2:
    st.subheader("Rep Harakah")
    st.dataframe(rep_haraka, use_container_width=True)


# =========================
# 📊 CLIENT HARKA
# =========================
with tab3:
    st.subheader("Client Harakah")

    # فلترة بالمندوب
    reps = client_haraka["Rep Name"].dropna().unique()
    selected_rep = st.selectbox("Filter by Rep", ["All"] + list(reps))

    if selected_rep != "All":
        df_client = client_haraka[client_haraka["Rep Name"] == selected_rep]
    else:
        df_client = client_haraka

    st.dataframe(df_client, use_container_width=True)
