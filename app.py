import pandas as pd
import re

# -------------------------------------------------------------------------------------
# Read Excel File
# -------------------------------------------------------------------------------------

file_name = "Visit List.xlsx"
df = pd.read_excel(file_name)

df.columns = df.columns.str.strip()

# -------------------------------------------------------------------------------------
# Fix Client Type spelling issue
# -------------------------------------------------------------------------------------

df['Client Type'] = df['Client Type'].replace({
    'Prescriper': 'Prescriber'
})

# -------------------------------------------------------------------------------------
# Convert Date
# -------------------------------------------------------------------------------------

df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df = df.dropna(subset=['Date'])

df['Month'] = df['Date'].dt.month

# فلترة أول 3 شهور
df = df[df['Month'].isin([1, 2, 3])]

# -------------------------------------------------------------------------------------
# Clean sheet name
# -------------------------------------------------------------------------------------

def clean_sheet_name(name):
    name = str(name)
    name = re.sub(r'[\\/*?:\[\]]', '_', name)
    return name[:31]

# -------------------------------------------------------------------------------------
# Output file
# -------------------------------------------------------------------------------------

output_file = "Visits_Per_Rep_Q1_Sorted.xlsx"

with pd.ExcelWriter(output_file, engine='openpyxl') as writer:

    for rep in df['Full Name'].dropna().unique():

        rep_df = df[df['Full Name'] == rep]

        # =================================================================================
        # 1) ACCOUNT TABLE
        # =================================================================================

        summary = rep_df.groupby(['Account', 'Month']).size().reset_index(name='Visits')

        pivot_table = summary.pivot_table(
            index='Account',
            columns='Month',
            values='Visits',
            fill_value=0
        )

        # Ensure months exist
        for m in [1, 2, 3]:
            if m not in pivot_table.columns:
                pivot_table[m] = 0

        pivot_table = pivot_table[[1, 2, 3]]

        pivot_table = pivot_table.rename(columns={
            1: 'Month 1',
            2: 'Month 2',
            3: 'Month 3'
        })

        pivot_table = pivot_table.astype(int)

        pivot_table['Total Visits'] = pivot_table.sum(axis=1)

        pivot_table = pivot_table.sort_values(by='Total Visits', ascending=False)

        # ---------------------------------------------------------------------------------
        # Distribution
        # ---------------------------------------------------------------------------------

        dist_counts = {
            '1 Visit': (pivot_table['Total Visits'] == 1).sum(),
            '2 Visits': (pivot_table['Total Visits'] == 2).sum(),
            '3 Visits': (pivot_table['Total Visits'] == 3).sum(),
            '4 Visits': (pivot_table['Total Visits'] == 4).sum(),
            '5 Visits': (pivot_table['Total Visits'] == 5).sum(),
            '>5 Visits': (pivot_table['Total Visits'] > 5).sum(),
        }

        dist_df = pd.DataFrame(
            list(dist_counts.items()),
            columns=['Category', 'Client Count']
        )

        # =================================================================================
        # 2) CLIENT TYPE TABLE
        # =================================================================================

        client_summary = rep_df.groupby(['Client Type', 'Month']).size().reset_index(name='Visits')

        client_pivot = client_summary.pivot_table(
            index='Client Type',
            columns='Month',
            values='Visits',
            fill_value=0
        )

        for m in [1, 2, 3]:
            if m not in client_pivot.columns:
                client_pivot[m] = 0

        client_pivot = client_pivot[[1, 2, 3]]

        client_pivot = client_pivot.rename(columns={
            1: 'Jan',
            2: 'Feb',
            3: 'Mar'
        })

        client_pivot = client_pivot.astype(int)

        # Total Visits per Client Type
        client_pivot['Total Visits'] = client_pivot[['Jan', 'Feb', 'Mar']].sum(axis=1)

        # Correct order
        order = ['Retail', 'End User', 'Prescriber']
        client_pivot = client_pivot.reindex(order)

        # =================================================================================
        # WRITE TO EXCEL
        # =================================================================================

        sheet_name = clean_sheet_name(rep)

        # ---- Table 1 (Accounts)
        pivot_table.to_excel(
            writer,
            sheet_name=sheet_name,
            startrow=0,
            startcol=0
        )

        # ---- Distribution
        dist_df.to_excel(
            writer,
            sheet_name=sheet_name,
            startrow=0,
            startcol=pivot_table.shape[1] + 3,
            index=False
        )

        # ---- Table 2 (Client Type)
        client_pivot.to_excel(
            writer,
            sheet_name=sheet_name,
            startrow=0,
            startcol=pivot_table.shape[1] + 10
        )

print("File Created Successfully ✅")

