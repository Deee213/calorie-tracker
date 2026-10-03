import pandas as pd
import glob
import os

# Path to the folder containing your CSV files
folder_path = "C:\\Users\\SMS1\\Documents\\Ed Files\\Gather\\Feeder 2"

# Get all CSV files in the folder
csv_files = glob.glob(os.path.join(folder_path, "*.csv"))

print(f"Found {len(csv_files)} CSV files:", csv_files)

# Read each CSV WITHOUT headers
dataframes = [pd.read_csv(f, header=None) for f in csv_files]

# Merge them together
merged_df = pd.concat(dataframes, ignore_index=True)

# Save merged CSV into the same folder, no headers, no index
output_path = os.path.join(folder_path, "Feeder2.csv")
merged_df.to_csv(output_path, index=False, header=False)

print(f"Merging complete! Saved as {output_path}")