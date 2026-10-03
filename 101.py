import pandas as pd

# Load the original Excel file
df = pd.read_excel("C:\\Users\\SMS1\\Documents\\Ed Files\\Synergi\\Villa Kananga\\Feeder 2\\New folder\\Feeder2 Poles VK.xlsx", sheet_name="feeder2_pole_vk")

# Extract Pole number and Coordinates
objectid = df["OBJECTID"]   # fixed typo
x = df["X"]
y = df["Y"]

# Create new DataFrame with desired format
new_df = pd.DataFrame({
    "Column 1": 101,
    "Column 2": objectid,
    "Latitude": x,
    "Longitude": y
})

# Save to CSV file
new_df.to_csv("C:\Users\SMS1\Documents\Ed Files\Synergi\Villa Kananga\Feeder 2\Exam\EXAM6.csv", index=False)

print("Done! File saved as 101.csv")