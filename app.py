import pandas as pd
import numpy as np

# =========================
# 🧹 REMOVE EMPTY ROWS
# =========================
def remove_empty_rows(data):

    def clean(df):
        # حذف الصفوف اللي كلها NaN
        df = df.dropna(how="all")

        # حذف الصفوف اللي فيها فراغات نصية فقط
        df = df.replace(r'^\s*$', np.nan, regex=True)
        df = df.dropna(how="all")

        return df

    data["sales"] = clean(data["sales"])
    data["opening"] = clean(data["opening"])
    data["overdue"] = clean(data["overdue"])

    # targets (اختياري لو فيها فراغات)
    for key in ["target_rep", "target_manager", "target_area", "target_supervisor", "target_evak"]:
        data[key] = clean(data[key])

    return data


# =========================
# ▶️ FULL PIPELINE
# =========================
if __name__ == "__main__":

    data = load_data()
    data = rename_columns(data)
    data = add_columns(data)
    data = remove_empty_rows(data)

    print("✔️ Load → Rename → Add Columns → Clean Empty Rows Done")
