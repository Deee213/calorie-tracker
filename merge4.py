import glob
import os

# 1. Set the folder where your CSV files are stored
folder_path = "C:\\Users\Ed\\Documents\\ANECO\\Feeder 1 Try"

# 2. Find all CSV files in the folder
csv_files = glob.glob(os.path.join(folder_path, "*.csv"))

# 3. Merge them into one file (skip headers)
output_file = os.path.join(folder_path, "merged.csv")

with open(output_file, "w", encoding="utf-8") as outfile:
    for fname in csv_files:
        with open(fname, "r", encoding="utf-8") as infile:
            # Skip the header line of each file
            infile.readline()
            # Append the rest of the file
            outfile.write(infile.read())

print(f"Merged {len(csv_files)} files into {output_file} (headers removed)")