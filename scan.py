import fitz  # PyMuPDF
import pytesseract
import pandas as pd
import io
import re
import os
from PIL import Image

# ==========================================
# 1. CONFIGURATION
# ==========================================
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

INPUT_PDF = r"\\192.168.5.4\AMFMReport\ARIEL\00-2026-capex\CAPEX2024-2025\capex2024-2025-12022025\CAPEX2024-2025\Pangilinan\PROJECT 1\PR01-MCTA008197.pdf"
OUTPUT_FILE = r"C:\Users\SMS1\Documents\69\1xtracted_data.csv"

def extract_numbers_from_row(text_list):
    """Finds numbers with decimals in the list of text found on one line."""
    # Pattern for numbers like 1,234.5678 or 1234.56
    nums = [re.sub(r'[^-0-9.]', '', x) for x in text_list if re.search(r'\d+\.\d+', x)]
    return nums

def extract_ticket_data_alternate(pdf_path):
    if not os.path.exists(pdf_path):
        print("File path not found.")
        return pd.DataFrame()

    doc = fitz.open(pdf_path)
    page = doc[0]
    pix = page.get_pixmap(dpi=300)
    img = Image.open(io.BytesIO(pix.tobytes("png")))

    # Get OCR data as a list of lines
    # Using --psm 6 to preserve the table structure as much as possible
    raw_text = pytesseract.image_to_string(img, config='--psm 6')
    
    rows = []
    lines = raw_text.split('\n')
    
    # regex pattern for your Item Codes (e.g., 0094-50-30A or 0215-02-00)
    item_code_pattern = r'\d{4}-\d{2}-[0-9A-Z]{2,3}'

    for line in lines:
        # Check if the line contains an Item Code
        match = re.search(item_code_pattern, line)
        if match:
            item_code = match.group()
            
            # Split the line by spaces to find the numbers
            parts = line.split()
            
            # We look for all pieces that look like numbers (Quantity, Unit Cost, Total Cost)
            numeric_parts = extract_numbers_from_row(parts)
            
            # Based on your ticket layout:
            # numeric_parts[0] = Quantity (e.g., 2.00)
            # numeric_parts[-2] = Unit Cost
            # numeric_parts[-1] = Total Cost
            if len(numeric_parts) >= 3:
                rows.append({
                    "item_code": item_code,
                    "qty": numeric_parts[0],
                    "unit": "pcs." if "pcs" in line.lower() else ("mtrs." if "mtr" in line.lower() else "ft."),
                    "unit_cost": numeric_parts[-2],
                    "total_cost": numeric_parts[-1]
                })

    return pd.DataFrame(rows)

# ==========================================
# 2. EXECUTION
# ==========================================
try:
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    final_df = extract_ticket_data_alternate(INPUT_PDF)
    
    if not final_df.empty:
        # Ensure the columns are in the exact order you want
        final_df = final_df[['item_code', 'qty', 'unit', 'unit_cost', 'total_cost']]
        
        final_df.to_csv(OUTPUT_FILE, index=False)
        print("Success! Data extracted using pattern matching.")
        print(final_df.to_string(index=False))
    else:
        print("No items found matching the Item Code pattern.")

except Exception as e:
    print(f"An error occurred: {e}")