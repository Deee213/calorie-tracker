import pandas as pd

# --- Load the three Excel files with your specified paths ---
df_line = pd.read_excel("\\192.168.5.4\AMFMReport\999 ED FILES\DSAS\DSAS FEEDER 2\Excel Files\Feeder2 Consumer_Line.xlsx")
df_customer = pd.read_excel("\\192.168.5.4\AMFMReport\999 ED FILES\DSAS\DSAS FEEDER 2\Excel Files\Feeder2_ConsumerDataPoint.xlsx")
df_billing = pd.read_excel("C:\\Users\\SMS1\\Documents\\Ed Files\\Synergi\\Consumer Billing.xlsx")

# --- Normalize account numbers for matching ---
df_customer["Account__"] = df_customer["Account__"].astype(str).str.strip()
df_billing["AcctNumber"] = df_billing["AcctNumber"].astype(str).str.strip()

# --- Phase indicators with special case for "ABC" ---
phase_a = []
phase_b = []
phase_c = []

for ph in df_line["Phase"]:
    if ph == "A":
        phase_a.append(1)
        phase_b.append(0)
        phase_c.append(0)
    elif ph == "B":
        phase_a.append(0)
        phase_b.append(1)
        phase_c.append(0)
    elif ph == "C":
        phase_a.append(0)
        phase_b.append(0)
        phase_c.append(1)
    elif ph == "ABC":
        # distribute equally
        phase_a.append(0.333)
        phase_b.append(0.333)
        phase_c.append(0.333)
    else:
        phase_a.append(0)
        phase_b.append(0)
        phase_c.append(0)

phase_a = pd.Series(phase_a)
phase_b = pd.Series(phase_b)
phase_c = pd.Series(phase_c)

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

# --- Build final DataFrame ---
new_df = pd.DataFrame({
    "Column 1": 502,                       # constant
    "Column 2": df_line["OBJECTID"],       # OBJECTID from Customer Line
    "Column 3": phase_a,                   # Phase A indicator
    "Column 4": phase_b,                   # Phase B indicator
    "Column 5": phase_c,                   # Phase C indicator
    "Column 6": col6,                      # ConsKWH if Phase A
    "Column 7": col7,                      # ConsKWH if Phase B
    "Column 8": col8                       # ConsKWH if Phase C
})


# --- Save to Excel ---
output_file = "\\192.168.5.4\AMFMReport\999 ED FILES\DSAS\DSAS FEEDER 2\Excel Files\502.csv"
new_df.to_excel(output_file, index=False)

print(f"Done! File saved as {output_file}")