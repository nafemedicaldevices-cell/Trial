import pandas as pd
import numpy as np

def build_dashboard(targets, sales, codes, level, selected_code):

    # =========================
    # 🔗 FILTER TARGETS
    # =========================
    target_df = targets[level]

    target_df = target_df.merge(
        codes,
        on="Code",
        how="left"
    )

    target_df = target_df[
        target_df["Rep Code"] == selected_code
    ]

    # =========================
    # 🔗 FILTER SALES
    # =========================
    sales = sales[
        sales["Rep Code"].astype(str).str.strip() == str(selected_code).strip()
    ]

    # =========================
    # 📊 GROUP SALES BY PRODUCT
    # =========================
    sales_agg = sales.groupby(
        "Product Name", as_index=False
    ).agg({
        "Sales Unit": "sum",
        "Sales Value": "sum"
    })

    # =========================
    # 📊 TARGET AGG
    # =========================
    target_agg = target_df.groupby(
        "Old Product Name", as_index=False
    ).agg({
        "Target (Unit)": "sum",
        "Target (Value)": "sum"
    })

    # =========================
    # 🔗 MERGE
    # =========================
    df = target_agg.merge(
        sales_agg,
        left_on="Old Product Name",
        right_on="Product Name",
        how="left"
    )

    df["Sales Unit"] = df["Sales Unit"].fillna(0)
    df["Sales Value"] = df["Sales Value"].fillna(0)

    # =========================
    # 📊 ACHIEVEMENT %
    # =========================
    df["Achievement Unit %"] = np.where(
        df["Target (Unit)"] > 0,
        df["Sales Unit"] / df["Target (Unit)"],
        0
    )

    df["Achievement Value %"] = np.where(
        df["Target (Value)"] > 0,
        df["Sales Value"] / df["Target (Value)"],
        0
    )

    # =========================
    # FINAL SHAPE
    # =========================
    df = df[[
        "Old Product Name",
        "Target (Unit)",
        "Sales Unit",
        "Achievement Unit %",
        "Target (Value)",
        "Sales Value",
        "Achievement Value %"
    ]]

    df.columns = [
        "Product Name",
        "Target Unit",
        "Sales Unit",
        "Achievement Unit %",
        "Target Value",
        "Sales Value",
        "Achievement Value %"
    ]

    return df
