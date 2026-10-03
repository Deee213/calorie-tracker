import pandas as pd

# --- Load source files ---
pole_df = pd.read_excel(
    r"C:\Users\Ed\Documents\CBR Feeder 2 Test\Feeder2CBR Poles.xlsx",
    sheet_name="feeder2cbr_poles")
line_df = pd.read_excel(
    r"C:\Users\Ed\Documents\CBR Feeder 2 Test\Feeder2CBR Lines.xlsx",
    sheet_name="feeder2cbr_lines"
)

# --- Filter jumpers ---
jumpers = line_df[line_df["Line_Type"] == "Jumper"].copy()

# --- Ensure IDs are strings for matching ---
jumpers["Y_ID"] = jumpers["Y_ID"].astype(str)
jumpers["X_ID"] = jumpers["X_ID"].astype(str)
pole_df["OBJECTID"] = pole_df["OBJECTID"].astype(str)

# --- Merge jumper lines with pole data ---
merged = pd.merge(
    jumpers[["OBJECTID", "Y_ID", "X_ID", "Phase"]],
    pole_df[["OBJECTID", "Trans_numb", "Trans_KVA", "X", "Y"]],
    left_on="Y_ID",
    right_on="OBJECTID",
    how="left"
)

# --- Build final DataFrame (new structure) ---
final_df = pd.DataFrame({
    "Code": 2010,                                # column 1 (updated constant)
    "Line_ObjectID": merged["OBJECTID_x"],       # column 2
    "Trans_Numb": merged["Trans_numb"],          # column 3
    "Trans_KVA": merged["Trans_KVA"],            # column 4 (moved from old col8)
    "Col5": "Yg",                                # column 5 = constant "Yg"
    "Col6": "Yg"                                 # column 6 = constant "Yg"
})

# --- Save to CSV ---
final_df.to_csv(
    r"C:\Users\Ed\Documents\CBR Feeder 2 Test\2010.csv",
    index=False
)

print("Done! File saved as 2010.csv")
