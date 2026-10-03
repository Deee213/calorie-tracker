import pandas as pd

# Read Excel file
df = pd.read_excel(
    r"C:\\Users\\SMS1\\Documents\\Ed Files\\Synergi\\Villa Kananga\\Feeder 1\\New Folder\\Feeder1 Pole VK.xlsx", sheet_name="added_fields"
)

# Filter rows where Remarks == "Source"
Source = df[df["Remarks"] == "Source"].copy()

# Extract OBJECTID and Substation values
objectids = Source["OBJECTID"].tolist()
substations = Source["Substation"].tolist()

# Build new DataFrame with all required columns
new_df = pd.DataFrame({
    "Column 1": [301] * len(objectids),   # constant 301
    "Column 2": objectids,                # OBJECTID values
    "Column 3": [13.2] * len(objectids),  # constant 13.2
    "Column 4": [240] * len(objectids),   # constant 120
    "Column 5": ["Yg"] * len(objectids),  # constant string "Yg"
    "Column 6": substations               # values from Substation column
})

# Export to CSV (full file)
output_path = r"C:\\Users\\SMS1\\Documents\\Ed Files\\Synergi\\Villa Kananga\\Feeder 1\\New Folder\\301.csv"
new_df.to_csv(output_path, index=False)

print(f"CSV file created at: {output_path}")