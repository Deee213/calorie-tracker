import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import subprocess  # To open the folder after conversion

# Try to import Pillow for image handling
try:
    from PIL import Image, ImageTk
except ImportError:
    import sys
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Missing Library", "Please install Pillow to use the background image:\npip install pillow")
    sys.exit()

# --- BUSINESS LOGIC ---

def load_excel_flexible(file_path, target_sheet_name):
    """Loads sheet by name case-insensitively or defaults to the first sheet."""
    try:
        xl = pd.ExcelFile(file_path)
        sheet_names = xl.sheet_names
        found_sheet = next((s for s in sheet_names if s.lower() == target_sheet_name.lower()), None)
        return pd.read_excel(xl, sheet_name=found_sheet if found_sheet else 0)
    except Exception as e:
        raise Exception(f"Excel Error: {str(e)}")

def get_col(df, target):
    """Finds column name regardless of capitalization."""
    mapping = {col.lower(): col for col in df.columns}
    if target.lower() in mapping:
        return df[mapping[target.lower()]]
    raise KeyError(f"Missing Column: {target}")

def process_files(pole_path, line_path, save_path):
    """Combines all GIS logic into one CSV."""
    try:
        pole_df = load_excel_flexible(pole_path, "Poles")
        line_df = load_excel_flexible(line_path, "Lines")
        all_data = []

        # Logic 101: Pole Locations
        all_data.append(pd.DataFrame({
            "A": [101] * len(pole_df),
            "B": get_col(pole_df, "OBJECTID"),
            "C": get_col(pole_df, "X"),
            "D": get_col(pole_df, "Y")
        }))

        # Logic 201: Connectivity
        all_data.append(pd.DataFrame({
            "A": [201] * len(line_df),
            "B": get_col(line_df, "OBJECTID"),
            "C": get_col(line_df, "X_ID"),
            "D": get_col(line_df, "Y_ID")
        }))

        # Logic 203: Phasing & Conductor
        p_map = {"ABC": 7, "A": 1, "B": 2, "C": 3, "AB": 4, "BC": 5, "CA": 6}
        phasing = get_col(line_df, "Phase").map(p_map).fillna(7)
        all_data.append(pd.DataFrame({
            "A": [203] * len(line_df),
            "B": get_col(line_df, "OBJECTID"),
            "C": phasing,
            "D": get_col(line_df, "SHAPE_Leng"),
            "E": get_col(line_df, "Con_size"),
            "F": get_col(line_df, "Neu_size"),
            "G": phasing.apply(lambda x: 4 if x==7 else (3 if x>3 else 2))
        }))

        # Logic 301: Source filtering
        remarks = get_col(pole_df, "Remarks")
        src = pole_df[remarks.astype(str).str.lower() == "source"].copy()
        if not src.empty:
            all_data.append(pd.DataFrame({
                "A": [301] * len(src),
                "B": get_col(src, "OBJECTID"),
                "C": 13.2, "D": 120, "E": "Yg",
                "F": get_col(src, "Substation")
            }))

        # Logic 1301: Transformers matched with Jumpers
        l_type = get_col(line_df, "Line_type")
        jumpers = line_df[l_type.astype(str).str.lower() == "jumper"].copy()
        if not jumpers.empty:
            j_yid = get_col(jumpers, "Y_ID").astype(str)
            p_id = get_col(pole_df, "OBJECTID").astype(str)
            merged = pd.merge(jumpers, pole_df, left_on=j_yid.name, right_on=p_id.name, how="left")
            all_data.append(pd.DataFrame({
                "A": [1301] * len(merged),
                "B": get_col(merged, "OBJECTID_x"),
                "C": get_col(merged, "Trans_numb"),
                "D": get_col(merged, "Trans_KVA"),
                "E": 0, "F": 1, "G": "Yg", "H": "Yg"
            }))

        final = pd.concat(all_data, ignore_index=True)
        final.to_csv(save_path, index=False, header=False)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Conversion Failed:\n{str(e)}")
        return False

# --- UI CLASS ---

class SynergiApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Synergi Converter")
        self.geometry("450x700")
        self.resizable(False, False)

        # Background Image Path
        img_path = r"C:\Users\Ed\Documents\ANECO\Synergi Codes\rm251-mind-08-f.jpg"
        
        if os.path.exists(img_path):
            try:
                self.bg_image = Image.open(img_path)
                self.bg_image = self.bg_image.resize((450, 700), Image.LANCZOS)
                self.bg_photo = ImageTk.PhotoImage(self.bg_image)
                self.canvas = tk.Canvas(self, width=450, height=700)
                self.canvas.pack(fill="both", expand=True)
                self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
            except:
                self.use_fallback()
        else:
            self.use_fallback()

        self.create_widgets()

    def use_fallback(self):
        self.canvas = tk.Canvas(self, width=450, height=700, bg="#0F172A")
        self.canvas.pack(fill="both", expand=True)

    def create_widgets(self):
        self.canvas.create_text(225, 80, text="⚡ SYNERGI CONVERTER", fill="white", font=("Arial", 22, "bold"))
        self.canvas.create_text(225, 115, text="Data Transformation Engine", fill="#94A3B8", font=("Arial", 10))
        self.canvas.create_rectangle(40, 160, 410, 520, fill="#1E293B", outline="#334155")

        self.create_input_group(210, "📄 Select Pole Excel File", self.select_pole, "pole_label")
        self.create_input_group(340, "📄 Select Line Excel File", self.select_line, "line_label")

        self.gen_btn = tk.Button(self, text="🧮 Generate CSV", command=self.run_conversion, 
                                 bg="#10B981", fg="white", font=("Arial", 12, "bold"), 
                                 relief="flat", width=22, height=2, cursor="hand2")
        self.canvas.create_window(225, 470, window=self.gen_btn)

        self.status_label = tk.Label(self, text="Ready", bg="#0F172A", fg="#94A3B8")
        self.canvas.create_window(225, 680, window=self.status_label, width=450)

    def create_input_group(self, y_pos, label_text, cmd, tag):
        self.canvas.create_text(60, y_pos, text=label_text, fill="#CBD5E1", anchor="w")
        btn = tk.Button(self, text="UPLOAD", command=cmd, bg="#334155", fg="white", relief="flat")
        self.canvas.create_window(360, y_pos, window=btn)
        
        preview = tk.Label(self, text="No file selected", bg="#1E293B", fg="#64748B", font=("Arial", 8))
        self.canvas.create_window(225, y_pos + 40, window=preview, width=320)
        setattr(self, tag, preview)

    def select_pole(self):
        path = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx")])
        if path:
            self.pole_path = path
            self.pole_label.config(text=os.path.basename(path), fg="#10B981")

    def select_line(self):
        path = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx")])
        if path:
            self.line_path = path
            self.line_label.config(text=os.path.basename(path), fg="#10B981")

    def run_conversion(self):
        if not hasattr(self, 'pole_path') or not hasattr(self, 'line_path'):
            self.status_label.config(text="⚠️ Please select both files.")
            return
        
        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if save_path:
            if process_files(self.pole_path, self.line_path, save_path):
                self.status_label.config(text="✅ Success!", fg="#10B981")
                messagebox.showinfo("Success", f"File Exported!\nOpening folder...")
                
                # Automatically open the folder containing the file
                folder_path = os.path.dirname(os.path.abspath(save_path))
                if os.name == 'nt':  # For Windows
                    os.startfile(folder_path)
                else:  # For Mac/Linux
                    subprocess.run(['open', folder_path] if sys.platform == 'darwin' else ['xdg-open', folder_path])

if __name__ == "__main__":
    app = SynergiApp()
    app.mainloop()