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

INPUT_FOLDER = r"\\192.168.5.4\AMFMReport\ARIEL\00-2026-capex\CAPEX2024-2025\capex2024-2025-12022025\CAPEX2024-2025\Pangilinan\PROJECT 1"
OUTPUT_FILE = r"C:\Users\SMS1\Documents\69\combined_extracted_data.csv"

def format_item_code(text):
    """Formats item code to include dashes (e.g., 0094-50-30a)."""
    if not text: return ""
    # Standardize common OCR misreads
    text = text.replace("0215", "0245").replace("1171-11", "1171-14")
    # Remove existing dashes to re-format cleanly
    clean = re.sub(r'[^a-z0-9]', '', text.lower())
    
    # Apply ####-##-## format if the string is long enough
    if len(clean) >= 8:
        return f"{clean[:4]}-{clean[4:6]}-{clean[6:]}"
    return clean

def clean_numeric(text):
    if not text: return "0.00"
    match = re.search(r'\d+\.\d+', text.replace(' ', ''))
    return match.group() if match else "0.00"

def process_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        page = doc[0]
        pix = page.get_pixmap(dpi=500)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        
        data = pytesseract.image_to_data(img, config='--psm 6', output_type=pytesseract.Output.DICT)
        
        columns = {
            "item_code": (100, 850),
            "qty": (2200, 2650),
            "unit": (2651, 2950),
            "unit_cost": (2951, 3550),
            "total_cost": (3551, 4300)
        }
        
        words = []
        for i in range(len(data['text'])):
            text = data['text'][i].strip()
            if not text: continue
            x, y, h = data['left'][i], data['top'][i], data['height'][i]
            
            if 1400 < y < 4100:
                for col_name, (start, end) in columns.items():
                    if start <= x <= end:
                        words.append({'y': y + (h/2), 'col': col_name, 'text': text})

        if not words: return pd.DataFrame()

        df_words = pd.DataFrame(words).sort_values('y')
        rows = []
        current_group = []
        if not df_words.empty:
            last_y = df_words.iloc[0]['y']
            for _, word in df_words.iterrows():
                if word['y'] - last_y > 35:
                    if current_group: rows.append(current_group)
                    current_group = [word]
                else:
                    current_group.append(word)
                last_y = word['y']
            rows.append(current_group)

        file_rows = []
        for r in rows:
            row_dict = {col: " ".join([w['text'] for w in r if w['col'] == col]) for col in columns}
            if re.search(r'\d', row_dict['item_code']):
                file_rows.append({
                    "file_name": os.path.basename(pdf_path),
                    "item_code": format_item_code(row_dict['item_code']),
                    "qty": clean_numeric(row_dict['qty']),
                    "unit": "pcs." if "0094" in row_dict['item_code'] else "ft.",
                    "unit_cost": clean_numeric(row_dict['unit_cost']),
                    "total_cost": clean_numeric(row_dict['total_cost'])
                })
        doc.close()
        return pd.DataFrame(file_rows)
    except Exception as e:
        return pd.DataFrame()

# ==========================================
# 2. EXECUTION
# ==========================================
all_dfs = []
files = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith('.pdf')]
for filename in files:
    df = process_pdf(os.path.join(INPUT_FOLDER, filename))
    if not df.empty:
        all_dfs.append(df)

if all_dfs:
    final_df = pd.concat(all_dfs, ignore_index=True)
    final_df.to_csv(OUTPUT_FILE, index=False)
    print(f"Extraction complete. Total rows: {len(final_df)}")