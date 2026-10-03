import pandas as pd

# Load the original Excel file
df = pd.read_excel("C:\\Users\\SMS1\\Documents\\Ed Files\\69\\Lines.xlsx", sheet_name="Sheet1")
   
# Create SectionID sequence
object_ids = df["OBJECTID"]

# Map phasing to numeric values
phase_map = {
    "ABC": 7,
    "A": 1,
    "B": 2,
    "C": 3,
    "AB": 4,
    "BC": 5,
    "CA": 6
}
phasing = df["Phase"].map(phase_map)

# Use Size of conductor for both phase and neutral
conductor = df["Con_Size"]
neutral = df["Neu_Size"]
length = df["SHAPE_Leng"]

# Define conductor runs based on phasing
def get_conductor_runs(p):
    if p in [1, 2, 3]:
        return 2
    elif p in [4, 5, 6]:
        return 3
    elif p == 7:
        return 4
    else:
        return None  # fallback if phasing is missing

conductor_runs = phasing.map(get_conductor_runs)

# Create new DataFrame with the extra column
new_df = pd.DataFrame({
    "Column 1": 203,
    "SectionID": object_ids,
    "Phasing": phasing,
    "Length": length,
    "Phase Conductor": conductor,
    "Neutral Conductor": neutral,
    "Conductor Runs": conductor_runs   # <-- new column added
})

# Save to CSV file
new_df.to_csv(
    "C:\\Users\\SMS1\\Documents\\Ed Files\\69\\203.csv",
    index=False
)

print("Done! File saved as 203.csv")