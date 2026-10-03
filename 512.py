import pandas as pd

# --- Load the three Excel files with your specified paths ---
df_line = pd.read_excel("C:\\Users\\SMS1\\Downloads\\Feeder2_Line_Customer_Villa_Kananga.xlsx")
df_customer = pd.read_excel("C:\\Users\\SMS1\\Downloads\\Feeder2_CustomerDataLocation_Villa_Kananga.xlsx")
df_billing = pd.read_excel("C:\\Users\\SMS1\\Documents\\Ed Files\\Synergi\\Consumer Billing.xlsx")

# --- Normalize account numbers for matching ---
df_customer["Account__"] = df_customer["Account__"].astype(str).str.strip()
df_billing["AcctNumber"] = df_billing["AcctNumber"].astype(str).str.strip()

# --- Lookup function for ConsKWH ---
def get_cons_kwh(y_id):
    # Step 1: find Customer row where OBJECTID == Y_ID
    cust_match = df_customer[df_customer["OBJECTID"] == y_id]
    if not cust_match.empty:
        account = cust_match.iloc[0]["Account__"]
        # Step 2: find Billing row where AcctNumber == account
        bill_match = df_billing[df_billing["AcctNumber"] == account]
        if not bill_match.empty:
            return bill_match.iloc[0]["ConsKWH"]
    return 0

# --- Build ConsKWH columns with special case for "ABC" ---
col6 = []  # ConsKWH if Phase A
col7 = []  # ConsKWH if Phase B
col8 = []  # ConsKWH if Phase C

for _, row in df_line.iterrows():
    cons_value = get_cons_kwh(row["Y_ID"])  # lookup consumption
    
    if row["Phase"] == "A":
        col6.append(cons_value)
        col7.append(0)
        col8.append(0)
    elif row["Phase"] == "B":
        col6.append(0)
        col7.append(cons_value)
        col8.append(0)
    elif row["Phase"] == "C":
        col6.append(0)
        col7.append(0)
        col8.append(cons_value)
    elif row["Phase"] == "ABC":
        # divide consumption equally across all three
        share = cons_value / 3
        col6.append(share)
        col7.append(share)
        col8.append(share)
    else:
        col6.append(0)
        col7.append(0)
        col8.append(0)

# --- Build final DataFrame (removed col3-col5, changed 502→512) ---
new_df = pd.DataFrame({
    "Column 1": 512,                       # constant updated
    "Column 2": df_line["OBJECTID"],       # OBJECTID from Customer Line
    "Column 6": col6,                      # ConsKWH if Phase A
    "Column 7": col7,                      # ConsKWH if Phase B
    "Column 8": col8                       # ConsKWH if Phase C
})

# --- Save to CSV instead of Excel ---
output_file = "C:\\Users\\SMS1\\Downloads\\512 - F2.csv"
new_df.to_csv(output_file, index=False)

print(f"Done! File saved as {output_file}")