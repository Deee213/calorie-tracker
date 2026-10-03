import pandas as pd

# Load both files
pole_df =pd.read_excel("C:\\Users\\SMS1\\Documents\\Ed Files\\Gather\\Feeder 2\\Feeder 2.xlsx", sheet_name="Poles")
line_df = pd.read_excel("C:\\Users\\SMS1\\Documents\\Ed Files\\Gather\\Feeder 2\\Feeder 2.xlsx", sheet_name="Lines")
jumpers = line_df[line_df["Line_Type"] == "Jumper"].copy()

# Ensure IDs are integers for matching
jumpers["Y_ID"] = jumpers["Y_ID"].astype(str)
pole_df["OBJECTID"] = pole_df["OBJECTID"].astype(str)

# Merge: match line.Y_ID with pole.OBJECTID
merged = pd.merge(
    jumpers[["OBJECTID", "Y_ID"]],
    pole_df[["OBJECTID", "Trans_numb", "Trans_KVA"]],
    left_on="Y_ID",
    right_on="OBJECTID",
    how="left"
)

# Build final DataFrame with all required columns
final_df = pd.DataFrame({
    "Code": 1301,
    "Line_ObjectID": merged["OBJECTID_x"],   # OBJECTID from line file
    "Trans_Numb": merged["Trans_numb"],      # from pole file
    "Trans_KVA": merged["Trans_KVA"],     # from pole file
    "Col5": 0,                               # constant 0
    "Col6": 1,                               # constant 1
    "Col7": "Yg",                            # constant Yg
    "Col8": "Yg"                             # constant Yg
})

# Save to CSV
final_df.to_csv("C:\\Users\\SMS1\\Documents\\Ed Files\\Gather\\Feeder 2\\1301.csv", index=False)
quoting=1

print("Done! File saved as 1301.csv")
