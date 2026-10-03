import os
import pandas as pd

# Source folder path
source_folder = r"\\192.168.5.4\AMFMReport\77 Pao Files\CapEx Files\Project 5 Replacement of Defective kWh Meters and Instrument Transformers\2024"

# Destination folder path
output_folder = r"\\192.168.5.4\AMFMReport\77 Pao Files\CapEx Files\Ed\PROJECT 5 - 2024"

# Collect file names
file_names = []
for file in os.listdir(source_folder):
    if os.path.isfile(os.path.join(source_folder, file)):
        # Remove extension first
        name_no_ext = os.path.splitext(file)[0]
        parts = name_no_ext.split("-")

        if len(parts) == 2:
            # Case 1: numeric prefix like "09740-1" → take first part
            if parts[0].isdigit():
                cleaned_name = parts[0]
            else:
                # Case 2: prefix like "PR01-MCTA009114" → take second part
                cleaned_name = parts[1]
            file_names.append(cleaned_name)

# Convert to DataFrame
df = pd.DataFrame(file_names, columns=["FileName"])

# Save to Excel in the destination folder
output_path = os.path.join(output_folder, "FileNames.xlsx")
df.to_excel(output_path, index=False)

print(f"Excel file created at: {output_path}")