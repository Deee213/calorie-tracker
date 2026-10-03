import pandas as pd

# --- Load source files ---
pole_df = pd.read_excel(
    r"C:\Users\Ed\Documents\CBR Feeder 2 Test\Feeder2CBR Poles.xlsx",
    sheet_name="feeder2cbr_poles")
line_df = pd.read_excel(
    r"C:\Users\Ed\Documents\CBR Feeder 2 Test\Feeder2CBR Lines.xlsx",
    sheet_name="feeder2cbr_lines"
)
billing_df = pd.read_excel(
    r"C:\Users\Ed\Documents\For testing\CustomerBilling data with feeders.xlsx",
    sheet_name="Sheet1"
)

# --- Normalize IDs ---
pole_df["OBJECTID"] = pole_df["OBJECTID"].astype(str).str.strip()
line_df["Y_ID"] = line_df["Y_ID"].astype(str).str.strip()
line_df["X_ID"] = line_df["X_ID"].astype(str).str.strip()

# Convert Load_Center_Id to numeric safely
billing_df["Load_Center_Id"] = pd.to_numeric(billing_df["Load_Center_Id"], errors="coerce")

# --- Filter jumpers ---
jumpers = line_df[line_df["Line_Type"] == "Jumper"].copy()

# --- Merge jumper lines with pole data ---
merged = pd.merge(
    jumpers[["OBJECTID", "Y_ID", "X_ID", "Phase"]],
    pole_df[["OBJECTID", "Trans_numb", "Trans_KVA", "X", "Y"]],
    left_on="Y_ID",
    right_on="OBJECTID",
    how="left"
)

# --- Normalize transformer numbers to numeric ---
merged["Trans_numb"] = pd.to_numeric(merged["Trans_numb"], errors="coerce")

# --- Phase mapping ---
phase_map = {"A": 1, "B": 2, "C": 3, "AB": 4, "BC": 5, "CA": 6, "ABC": 7}
merged["Phase_Code"] = merged["Phase"].map(phase_map)

# --- Merge with billing file (AcctName + ConsType) ---
final_with_billing = pd.merge(
    merged,
    billing_df[["Load_Center_Id", "AcctNumber", "ConsType"]],
    left_on="Trans_numb",
    right_on="Load_Center_Id",
    how="left"
)

# --- Consumer type mapping ---
cons_map = {
    "RE": "Residential",
    "CO": "Commercial",
    "IN": "Industrial"
}
final_with_billing["ConsType_Label"] = final_with_billing["ConsType"].map(cons_map)

# --- Build final DataFrame (Sheet1 only) ---
final_df = pd.DataFrame({
    "Code": 2002,
    "Line_ObjectID": final_with_billing["OBJECTID_x"],
    "Trans_Numb": final_with_billing["Trans_numb"],   # column 3
    "AcctNumber": final_with_billing["AcctNumber"],       # column 4
    "Phase_Code": final_with_billing["Phase_Code"],
    "Col6": 0,
    "X": final_with_billing["X"],
    "Y": final_with_billing["Y"],
    "ConsType_Label": final_with_billing["ConsType_Label"],  # mapped consumer type
    "Col11": 0  # new column with constant 0
})

# --- Save only one sheet ---
output_path = r"C:\Users\Ed\Documents\CBR Feeder 2 Test\2002.csv"
final_df.to_csv(output_path, index=False)

print("Done! File saved as 2002.csv")
