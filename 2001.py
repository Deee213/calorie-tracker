import pandas as pd

# Load both sheets
pole_df = pd.read_excel(
    r"C:\Users\SMS1\Documents\Ed Files\Synergi\Bayanihan\Feeder 5\Feeder3 Bayanihan Poles.xlsx",
    sheet_name="feeder_3_bayanihan"
)
line_df = pd.read_excel(
    r"C:\Users\SMS1\Documents\Ed Files\Synergi\Bayanihan\Feeder 5\Feeder3 Bayanihan Lines.xlsx",
    sheet_name="feeder_3_bayanihan_line"
)

# Filter jumpers
jumpers = line_df[line_df["Line_Type"] == "Jumper"].copy()

# Ensure IDs are strings for matching
jumpers["Y_ID"] = jumpers["Y_ID"].astype(str)
jumpers["X_ID"] = jumpers["X_ID"].astype(str)   # X_ID from line file
pole_df["OBJECTID"] = pole_df["OBJECTID"].astype(str)

# Merge: jumper.Y_ID ↔ pole.OBJECTID
merged = pd.merge(
    jumpers[["OBJECTID", "Y_ID", "X_ID", "Phase"]],   # <-- replace "Phase" with actual column name
    pole_df[["OBJECTID", "Trans_numb", "Trans_KVA", "X", "Y"]],
    left_on="Y_ID",
    right_on="OBJECTID",
    how="left"
)

# Phase mapping
phase_map = {
    "A": 1,
    "B": 2,
    "C": 3,
    "AB": 4,
    "BC": 5,
    "CA": 6,
    "ABC": 7
}
merged["Phase_Code"] = merged["Phase"].map(phase_map)   # <-- replace "Phase" with actual column name

# Build final DataFrame
final_df = pd.DataFrame({
    "Code": 2001,
    "Line_ObjectID": merged["OBJECTID_x"],   # OBJECTID from line file
    "Trans_Numb": merged["Trans_numb"],      # transformer number
    "Remarks": "Remarks",                    # constant
    "Phase_Code": merged["Phase_Code"],      # mapped phase
    "X_ID": merged["X_ID"],                  # X_ID from line file
    "X": merged["X"],                        # X coordinate from pole file
    "Y": merged["Y"],                        # Y coordinate from pole file
    "Trans_KVA": merged["Trans_KVA"],        # transformer KVA
    "Col9": 0                                # constant 0
})

# Save to CSV
final_df.to_csv(
    r"C:\Users\SMS1\Documents\Ed Files\Synergi\Bayanihan\Feeder 5\2001.csv",
    index=False
)

print("Done! File saved as 2001.csv")