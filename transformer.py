import pandas as pd

# Load your Excel file
df = pd.read_excel(r"C:\Users\SMS1\Documents\Ed Files\ALL TRANSFORMER.xlsx")

# Show available columns to confirm exact names
print("Available columns:", df.columns)

# Convert Trans_Numb column to string for safe matching
df["Trans_Numb"] = df["Trans_Numb"].astype(str).str.strip()

# Updated list of Trans_Numb values to filter (as strings)
filter_values = [
    "2811", "1310", "1782", "1252", "1339", "1449", "1064", "2706", "3631", "1742",
    "2273", "3640", "3961", "299", "1855", "221", "257", "621", "4929", "1028",
    "501", "1682", "1756", "4112", "3772", "4192", "546", "2417", "4266", "78",
    "277", "3281", "3470", "1439", "1709", "1733", "2847", "5614", "919", "2317",
    "5578", "6822", "1874", "1124", "5558", "1536", "4309", "297", "4013", "4014",
    "426", "569", "2671", "6270", "6497"
]

# Filter rows where Trans_Numb is in the list
filtered_df = df[df["Trans_Numb"].isin(filter_values)]

# Print filtered rows to console for quick verification
print("Filtered rows:")
print(filtered_df)

# Save the filtered results to a new Excel file
filtered_df.to_excel(r"C:\Users\SMS1\Documents\Ed Files\filter ALL TRANSFORMER.xlsx", index=False)

print("Filtered data saved to filter ALL TRANSFORMER.xlsx")