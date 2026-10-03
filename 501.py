import pandas as pd

# --- Load the three Excel files with your specified paths ---
df_line = pd.read_excel("C:\\Users\\SMS1\\Downloads\\Customer Line.xlsx")
df_customer = pd.read_excel("C:\\Users\\SMS1\\Downloads\\Customer.xlsx")
df_billing = pd.read_excel("C:\\Users\\SMS1\\Documents\\Ed Files\\Synergi\\Consumer Billing.xlsx")

# --- Normalize account numbers for matching ---
df_customer["Account__"] = df_customer["Account__"].astype(str).str.strip()
df_billing["AcctNumber"] = df_billing["AcctNumber"].astype(str).str.strip()

# --- Lookup functions ---
def get_cons_kw(y_id):
    cust_match = df_customer[df_customer["OBJECTID"] == y_id]
    if not cust_match.empty:
        account = cust_match.iloc[0]["Account__"]
        bill_match = df_billing[df_billing["AcctNumber"] == account]
        if not bill_match.empty and "ConsKW" in bill_match.columns:
            return bill_match.iloc[0]["ConsKW"]
    return 0

# --- Build columns ---
col3, col4, col5, col6, col7, col8 = [], [], [], [], [], []

for _, row in df_line.iterrows():
    if row["Phase"] == "A":
        val_kw = get_cons_kw(row["Y_ID"])
        col3.append(val_kw)          # ConsKW if Phase A
        col4.append(val_kw * 0.85)   # Column 3 × 0.85
        col5.append(0)
        col6.append(0)
        col7.append(0)
        col8.append(0)
    elif row["Phase"] == "B":
        val_kw = get_cons_kw(row["Y_ID"])
        col3.append(0)
        col4.append(0)
        col5.append(val_kw)          # ConsKW if Phase B
        col6.append(val_kw * 0.85)   # Column 5 × 0.85
        col7.append(0)
        col8.append(0)
    elif row["Phase"] == "C":
        val_kw = get_cons_kw(row["Y_ID"])
        col3.append(0)
        col4.append(0)
        col5.append(0)
        col6.append(0)
        col7.append(val_kw)          # ConsKW if Phase C
        col8.append(val_kw * 0.85)   # Column 7 × 0.85
    else:
        col3.append(0)
        col4.append(0)
        col5.append(0)
        col6.append(0)
        col7.append(0)
        col8.append(0)

# --- Build final DataFrame ---
new_df = pd.DataFrame({
    "Column 1": 502,                       # constant
    "Column 2": df_line["OBJECTID"],       # OBJECTID from Customer Line
    "Column 3": col3,                      # ConsKW if Phase A
    "Column 4": col4,                      # Column 3 × 0.85
    "Column 5": col5,                      # ConsKW if Phase B
    "Column 6": col6,                      # Column 5 × 0.85
    "Column 7": col7,                      # ConsKW if Phase C
    "Column 8": col8                       # Column 7 × 0.85
})


# --- Save to Excel ---
output_file = "C:\\Users\\SMS1\\Downloads\\Output_501.xlsx"
new_df.to_excel(output_file, index=False)

print(f"Done! File saved as {output_file}")