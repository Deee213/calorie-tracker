import pandas as pd

# Load both files
pole_df = pd.read_excel(
    r"C:\\Users\\SMS1\\Documents\\Ed Files\\Gather\\Feeder 2\\Feeder 2.xlsx",
    sheet_name="Poles"
)
line_df = pd.read_excel(
    r"C:\\Users\\SMS1\\Documents\\Ed Files\\Gather\\Feeder 2\\Feeder 2.xlsx", 
    sheet_name="Lines"
)

# Filter jumpers
jumpers = line_df[line_df["Line_Type"] == "Jumper"].copy()

# Ensure IDs are strings for matching
jumpers["Y_ID"] = jumpers["Y_ID"].astype(str)
pole_df["OBJECTID"] = pole_df["OBJECTID"].astype(str)

# Merge: match line.Y_ID with pole.OBJECTID
merged = pd.merge(
    jumpers[["OBJECTID", "Y_ID"]],
    pole_df[["OBJECTID"]],
    left_on="Y_ID",
    right_on="OBJECTID",
    how="left"
)

# Build final DataFrame with required columns
final_df = pd.DataFrame({
    "Code": 901,                           # first column
    "Line_ObjectID": merged["OBJECTID_x"], # second column
    "Fuse": ["FUSE-" + str(i+1) for i in range(len(merged))],  # third column
    "Const1": 1,                           # fourth column, constant 1
    "Const0": 0                            # fifth column, constant 0
})

# Convert any numeric columns to int (to drop .0)
for col in final_df.select_dtypes(include="number").columns:
    final_df[col] = final_df[col].astype(int)

# Save to CSV
final_df.to_csv(
    r"C:\\Users\\SMS1\\Documents\\Ed Files\\Gather\\Feeder 2\\901.csv",
    index=False
)

print("Done! File saved as 901.csv")