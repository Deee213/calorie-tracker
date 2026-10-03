import pandas as pd

# --- Load the three Excel files with your specified paths ---
df_line = pd.read_excel("C:\\Users\\SMS1\\Documents\\Ed Files\\Synergi\\Try\\Feeder2 Consumer_Line.xlsx")
df_customer = pd.read_excel("C:\\Users\SMS1\\Documents\\Ed Files\\Synergi\\Try\\Feeder2_ConsumerDataPoint.xlsx")
df_billing = pd.read_excel("C:\\Users\\SMS1\\Documents\\Ed Files\\Synergi\\Consumer Billing.xlsx")

# --- Normalize account numbers for matching ---
df_customer["Account__"] = df_customer["Account__"].astype(str).str.strip()
df_billing["AcctNumber"] = df_billing["AcctNumber"].astype(str).str.strip()

# --- Lookup function with ConsKWH fallback ---
def get_cons_kw(y_id):
    cust_match = df_customer[df_customer["OBJECTID"] == y_id]
    if not cust_match.empty:
        account = cust_match.iloc[0]["Account__"]
        bill_match = df_billing[df_billing["AcctNumber"] == account]
        if not bill_match.empty:
            # Prefer ConsKW if available
            if "ConsKW" in bill_match.columns and pd.notna(bill_match.iloc[0]["ConsKW"]):
                return bill_match.iloc[0]["ConsKW"]
            # Fallback: use ConsKWH ÷ 744 if available
            elif "ConsKWH" in bill_match.columns and pd.notna(bill_match.iloc[0]["ConsKWH"]):
                return bill_match.iloc[0]["ConsKWH"] / 744
    return 0

# --- Build columns ---
col4, col5, col6, col7, col8, col9 = [], [], [], [], [], []

for _, row in df_line.iterrows():
    if row["Phase"] == "A":
        val_kw = get_cons_kw(row["Y_ID"])
        col4.append(val_kw)          # ConsKW if Phase A
        col5.append(val_kw * 0.85)   # Column 4 × 0.85
        col6.append(0)
        col7.append(0)
        col8.append(0)
        col9.append(0)
    elif row["Phase"] == "B":
        val_kw = get_cons_kw(row["Y_ID"])
        col4.append(0)
        col5.append(0)
        col6.append(val_kw)          # ConsKW if Phase B
        col7.append(val_kw * 0.85)   # Column 6 × 0.85
        col8.append(0)
        col9.append(0)
    elif row["Phase"] == "C":
        val_kw = get_cons_kw(row["Y_ID"])
        col4.append(0)
        col5.append(0)
        col6.append(0)
        col7.append(0)
        col8.append(val_kw)          # ConsKW if Phase C
        col9.append(val_kw * 0.85)   # Column 8 × 0.85
    else:
        col4.append(0)
        col5.append(0)
        col6.append(0)
        col7.append(0)
        col8.append(0)
        col9.append(0)

# --- Build final DataFrame ---
new_df = pd.DataFrame({
    "Column 1": 504,                       # constant
    "Column 2": df_line["OBJECTID"],       # OBJECTID from Customer Line
    "Column 3": "T",                       # new constant column
    "Column 4": col4,                      # ConsKW if Phase A
    "Column 5": col5,                      # Column 4 × 0.85
    "Column 6": col6,                      # ConsKW if Phase B
    "Column 7": col7,                      # Column 6 × 0.85
    "Column 8": col8,                      # ConsKW if Phase C
    "Column 9": col9                       # Column 8 × 0.85
})

# --- Convert floats like 3100.0 → 3100 ---
# Apply a function to strip .0 if the value is an integer
def clean_number(x):
    if isinstance(x, float) and x.is_integer():
        return int(x)
    return x

new_df = new_df.applymap(clean_number)

# --- Save to CSV ---
output_file = "C:\\Users\\SMS1\\Documents\\Ed Files\\Synergi\Try\\504.csv"
new_df.to_csv(output_file, index=False)

print(f"Done! File saved as {output_file}")