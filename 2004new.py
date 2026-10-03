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

# --- Merge with billing file (AcctName + ConsKWH) ---
final_with_billing = pd.merge(
    merged,
    billing_df[["Load_Center_Id", "AcctNumber", "ConsKWH"]],
    left_on="Trans_numb",
    right_on="Load_Center_Id",
    how="left"
)

# --- Compute Col5 ---
final_with_billing["Col5"] = final_with_billing["ConsKWH"] / (720 * 0.7 * 0.9)

# --- Define Col9 as raw ConsKWH ---
final_with_billing["Col9"] = final_with_billing["ConsKWH"]

# --- Build final DataFrame ---
final_df = pd.DataFrame({
    "Code": 2004,
    "Line_ObjectID": final_with_billing["OBJECTID_x"],
    "Trans_Numb": final_with_billing["Trans_numb"],
    "AcctNumber": final_with_billing["AcctNumber"],
    "Col5": final_with_billing["Col5"],
    "Col6": 90,    # constant changed to 90
    "Col7": 1,     # constant
    "Col8": 1,     # constant
    "Col9": final_with_billing["Col9"]  # raw ConsKWH
})

# --- Save as CSV ---
output_path = r"C:\Users\Ed\Documents\CBR Feeder 2 Test\2004.csv"
final_df.to_csv(output_path, index=False)

print("Done! File saved as 2004.csv")
