import os
import shutil
import pandas as pd

# Source and destination paths
base_directory = r"\\192.168.5.4\AMFMReport\77 Pao Files\CapEx Files"
destination_directory = r"C:\Users\SMS1\Documents\Ed Files\CAPEX\CONSOLIDATED\PROJECT 3"

# Excel file containing numbers in Column B
excel_file = r"C:\Users\SMS1\Documents\Ed Files\CAPEX\CONSOLIDATED\List.xlsx"

# Read numbers from Column B (index 1)
df = pd.read_excel(excel_file)
numbers = set(df.iloc[:, 1].dropna().astype(str).tolist())  # use set for speed

def search_and_copy(base_dir, numbers, destination_dir, log_file="missing_numbers.txt"):
    os.makedirs(destination_dir, exist_ok=True)

    found_numbers = set()

    # Walk once through all files
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.lower().endswith(".pdf"):
                for number in numbers:
                    if number in file:
                        source_path = os.path.join(root, file)
                        dest_path = os.path.join(destination_dir, file)
                        shutil.copy2(source_path, dest_path)
                        print(f"Copied: {source_path} -> {dest_path}")
                        found_numbers.add(number)
                        break  # stop checking once matched

    # Compute missing numbers
    missing = numbers - found_numbers

    # Write missing numbers to log file
    log_path = os.path.join(destination_dir, log_file)
    with open(log_path, "w") as f:
        for num in sorted(missing):
            f.write(num + "\n")

    if missing:
        print(f"\nMissing numbers logged in: {log_path}")
    else:
        print("\nAll numbers were found and copied.")

if __name__ == "__main__":
    search_and_copy(base_directory, numbers, destination_directory)