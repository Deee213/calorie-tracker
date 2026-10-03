import pandas as pd

# --- Load the three Excel files with your specified paths ---
df_line = pd.read_excel("C:\\Users\\SMS1\\Downloads\\Feeder2_Line_Customer_Villa_Kananga.xlsx")
df_customer = pd.read_excel("C:\\Users\\SMS1\\Downloads\\Feeder2_CustomerDataLocation_Villa_Kananga.xlsx")
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

# --- Build final DataFrame (Column 1 changed to 509, removed col6-col8) ---
new_df = pd.DataFrame({
    "Column 1": 509,                       # constant updated
    "Column 2": df_line["OBJECTID"],       # OBJECTID from Customer Line
    "Column 3": phase_a,                   # Phase A indicator
    "Column 4": phase_b,                   # Phase B indicator
    "Column 5": phase_c                    # Phase C indicator
})

# --- Save to Excel ---
output_file = "C:\\Users\\SMS1\\Downloads\\509 - F2.csv"
new_df.to_csv(output_file, index=False)

print(f"Done! File saved as {output_file}")