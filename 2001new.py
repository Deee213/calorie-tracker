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
jumpers["X_ID"] = jumpers["X_ID"].astype(str)   # kept for merging, not in final output
pole_df["OBJECTID"] = pole_df["OBJECTID"].astype(str)

# --- Merge jumper lines with pole data ---
merged = pd.merge(
    jumpers[["OBJECTID", "Y_ID", "X_ID", "Phase"]],
    pole_df[["OBJECTID", "Trans_numb", "Trans_KVA", "X", "Y"]],
    left_on="Y_ID",
    right_on="OBJECTID",
    how="left"
)

# --- Phase mapping ---
phase_map = {
    "A": 1,
    "B": 2,
    "C": 3,
    "AB": 4,
    "BC": 5,
    "CA": 6,
    "ABC": 7
}
merged["Phase_Code"] = merged["Phase"].map(phase_map)

# --- Build final DataFrame (9 columns, no X_ID) ---
final_df = pd.DataFrame({
    "Code": 2001,                                # column 1
    "Line_ObjectID": merged["OBJECTID_x"],       # column 2
    "Trans_Numb": merged["Trans_numb"],          # column 3
    "Remarks": "Remarks",                        # column 4
    "Phase_Code": merged["Phase_Code"],          # column 5
    "X": merged["X"],                            # column 6
    "Y": merged["Y"],                            # column 7
    "Trans_KVA": merged["Trans_KVA"],            # column 8
    "Col9": 0                                    # column 9
})

# --- Save to CSV ---
final_df.to_csv(
    r"C:\Users\Ed\Documents\CBR Feeder 2 Test\2001.csv",
    index=False
)

print("Done! File saved as 2001.csv")