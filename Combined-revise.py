import pandas as pd

# Input and output paths
file_path = r"C:\Users\SMS1\Documents\Ed Files\CAPEX\03_PROJECT 5 - 2025.xlsx"
output_path = r"C:\Users\SMS1\Documents\Ed Files\CAPEX\03Combined_Project5_2025.xlsx"

# Load the Excel file
xls = pd.ExcelFile(file_path)

# --- First sheet ---
df1 = pd.read_excel(xls, sheet_name=0)
df1 = df1[["Description", "Pcs", "Unit Cost", "File Name"]].dropna(subset=["Description"])
df1 = df1.rename(columns={
    "Description": "ProductName",
    "Pcs": "Quantity",
    "Unit Cost": "UnitPrice",
    "File Name": "MCTNum"
})

# --- Second sheet ---
df2 = pd.read_excel(xls, sheet_name=1)
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
# Instead of grouping by ProductName + UnitPrice, group only by ProductName
# Compute a weighted average UnitPrice so totals match
aggregated = (
    df.groupby("ProductName", as_index=False)
      .agg({
          "Quantity": "sum",
          "UnitPrice": lambda x: (df.loc[x.index, "UnitPrice"] * df.loc[x.index, "Quantity"]).sum() / df.loc[x.index, "Quantity"].sum(),
          "MCTNum": lambda x: ",".join(map(str, x.unique()))
      })
)

# Round UnitPrice for neatness
aggregated["UnitPrice"] = aggregated["UnitPrice"].round(2)

# Save to new Excel file
aggregated.to_excel(output_path, index=False)

print(f"{output_path} created successfully!")