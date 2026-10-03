import pandas as pd

# Input and output paths
file_path = r"C:\Users\SMS1\Documents\Ed Files\CAPEX\0PROJECT 1 - 2023.xlsx"
output_path = r"C:\Users\SMS1\Documents\Ed Files\CAPEX\Consol_Project1_2023.xlsx"

# Load the Excel file
xls = pd.ExcelFile(file_path)

# --- First sheet ---
df1 = pd.read_excel(xls, sheet_name=0)
print("Sheet 1 headers:", df1.columns.tolist())

df1 = df1[["Description", "Pcs", "Unit Cost", "File Name"]].dropna(subset=["Description"])
df1 = df1.rename(columns={
    "Description": "ProductName",
    "Pcs": "Quantity",
    "Unit Cost": "UnitPrice",
    "File Name": "MCTNum"
})

# --- Second sheet ---
df2 = pd.read_excel(xls, sheet_name=1)
print("Sheet 2 headers:", df2.columns.tolist())

df2 = df2[["ProductName", "Quantity", "UnitPrice", "File Name"]].dropna(subset=["ProductName"])
df2 = df2.rename(columns={
    "ProductName": "ProductName",
    "Quantity": "Quantity",
    "UnitPrice": "UnitPrice",
    "File Name": "MCTNum"
})

# --- Combine both sheets ---
df = pd.concat([df1, df2], ignore_index=True)

# Clean ProductName
df["ProductName"] = df["ProductName"].astype(str).str.strip()

# --- Aggregate ---
aggregated = (
    df.groupby(["ProductName", "UnitPrice"], as_index=False)
      .agg({
          "Quantity": "sum",
          "MCTNum": lambda x: ",".join(map(str, x.unique()))
      })
)

# Save to new Excel file
aggregated.to_excel(output_path, index=False)

print(f"{output_path} created successfully!")