import pandas as pd

# Load the original Excel file
df = pd.read_excel("C:\\Users\\SMS1\\Downloads\\Customer_Feeder1_Line.xlsx", sheet_name="feeder2_line_customer_villa_kan")
from_pole = df["X_ID"]
to_pole = df["Y_ID"]

# Create SectionID as a sequence starting from 1
object_ids = df["OBJECTID"]

# Create new DataFrame with desired format
new_df = pd.DataFrame({
    "Column 1": 201,
    "OBJECTID": object_ids,
    "From Pole": from_pole,
    "To Pole": to_pole
})

# Save to CSV file
new_df.to_csv("C:\\Users\\SMS1\\Documents\\Ed Files\\Synergi\\VK\\Feeder 2\\201Cust.csv", index=False)

print("Done! File saved as 201.csv")