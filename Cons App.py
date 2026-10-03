import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd

# Constants & Mappings
PHASE_MAP = {"A": 1, "B": 2, "C": 3, "AB": 4, "BC": 5, "CA": 6, "ABC": 7}
CONS_MAP = {"RE": "Residential", "CO": "Commercial", "IN": "Industrial"}

STANDARD_COLUMNS = [
    "Code",             # Col 1
    "Line_ObjectID",    # Col 2
    "Trans_Numb",       # Col 3
    "AcctNumber",       # Col 4
    "Phase_Code",       # Col 5
    "Col6",             # Col 6
    "X",                # Col 7
    "Y",                # Col 8
    "ConsType_Label",   # Col 9
    "Trans_KVA",        # Col 10
    "Col11"             # Col 11
]

class FeederDataApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Feeder Data Processor")
        self.root.geometry("650x450")
        self.root.resizable(False, False)

        # File paths dictionary
        self.file_paths = {
            "pole": tk.StringVar(),
            "line": tk.StringVar(),
            "billing": tk.StringVar()
        }

        # Processed DataFrames storage
        self.processed_dfs = {}

        self.create_widgets()

    def create_widgets(self):
        # --- Title ---
        title_label = ttk.Label(self.root, text="⚡ Feeder Data Merger Tool", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=15)

        # --- File Selection Frame ---
        frame_files = ttk.LabelFrame(self.root, text=" 1. Select Input Excel Files ", padding=15)
        frame_files.pack(fill="x", padx=20, pady=5)

        # Pole File
        ttk.Label(frame_files, text="Poles File:").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(frame_files, textvariable=self.file_paths["pole"], width=50).grid(row=0, column=1, padx=5)
        ttk.Button(frame_files, text="Browse...", command=lambda: self.browse_file("pole")).grid(row=0, column=2)

        # Line File
        ttk.Label(frame_files, text="Lines File:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(frame_files, textvariable=self.file_paths["line"], width=50).grid(row=1, column=1, padx=5)
        ttk.Button(frame_files, text="Browse...", command=lambda: self.browse_file("line")).grid(row=1, column=2)

        # Billing File
        ttk.Label(frame_files, text="Billing File:").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(frame_files, textvariable=self.file_paths["billing"], width=50).grid(row=2, column=1, padx=5)
        ttk.Button(frame_files, text="Browse...", command=lambda: self.browse_file("billing")).grid(row=2, column=2)

        # --- Process Button ---
        self.btn_process = ttk.Button(self.root, text="🚀 Process Data", command=self.process_data)
        self.btn_process.pack(pady=15)

        # --- Export Actions Frame ---
        self.frame_export = ttk.LabelFrame(self.root, text=" 2. Export Datasets ", padding=15)
        self.frame_export.pack(fill="x", padx=20, pady=5)

        # Export Buttons (Initially Disabled)
        self.btn_export_individual = ttk.Button(
            self.frame_export, text="Export Individual CSVs (2001, 2002, 2004, 2010)", 
            command=self.export_individual, state="disabled"
        )
        self.btn_export_individual.pack(fill="x", pady=5)

        self.btn_export_merged = ttk.Button(
            self.frame_export, text="Export Single Master Merged CSV", 
            command=self.export_merged, state="disabled"
        )
        self.btn_export_merged.pack(fill="x", pady=5)

        # Status Bar
        self.status_var = tk.StringVar(value="Ready. Please select input files.")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w")
        status_bar.pack(side="bottom", fill="x", ipady=2)

    def browse_file(self, file_key):
        file_selected = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel Files", "*.xlsx *.xls")]
        )
        if file_selected:
            self.file_paths[file_key].set(file_selected)

    def process_data(self):
        # Validate file selections
        for key in ["pole", "line", "billing"]:
            if not self.file_paths[key].get():
                messagebox.showwarning("Missing File", f"Please select the {key.capitalize()} Excel file.")
                return

        try:
            self.status_var.set("Processing data... Please wait.")
            self.root.update_idletasks()

            # Read Excel files
            pole_df = pd.read_excel(self.file_paths["pole"].get(), sheet_name="feeder2cbr_poles")
            line_df = pd.read_excel(self.file_paths["line"].get(), sheet_name="feeder2cbr_lines")
            billing_df = pd.read_excel(self.file_paths["billing"].get(), sheet_name="Sheet1")

            # Clean keys
            pole_df["OBJECTID"] = pole_df["OBJECTID"].astype(str).str.strip()
            line_df["Y_ID"] = line_df["Y_ID"].astype(str).str.strip()
            line_df["X_ID"] = line_df["X_ID"].astype(str).str.strip()
            billing_df["Load_Center_Id"] = pd.to_numeric(billing_df["Load_Center_Id"], errors="coerce")

            # Filter jumpers & merges
            jumpers = line_df[line_df["Line_Type"] == "Jumper"].copy()

            base_merged = pd.merge(
                jumpers[["OBJECTID", "Y_ID", "X_ID", "Phase"]],
                pole_df[["OBJECTID", "Trans_numb", "Trans_KVA", "X", "Y"]],
                left_on="Y_ID",
                right_on="OBJECTID",
                how="left"
            )
            base_merged["Trans_numb"] = pd.to_numeric(base_merged["Trans_numb"], errors="coerce")
            base_merged["Phase_Code"] = base_merged["Phase"].map(PHASE_MAP)

            billing_merged = pd.merge(
                base_merged,
                billing_df[["Load_Center_Id", "AcctNumber", "ConsType", "ConsKWH"]],
                left_on="Trans_numb",
                right_on="Load_Center_Id",
                how="left"
            )
            billing_merged["ConsType_Label"] = billing_merged["ConsType"].map(CONS_MAP)

            # Generate Standardized DataFrames
            df_2001 = pd.DataFrame({
                "Code": 2001, "Line_ObjectID": base_merged["OBJECTID_x"],
                "Trans_Numb": base_merged["Trans_numb"], "AcctNumber": None,
                "Phase_Code": base_merged["Phase_Code"], "Col6": None,
                "X": base_merged["X"], "Y": base_merged["Y"],
                "ConsType_Label": 0, "Trans_KVA": base_merged["Trans_KVA"], "Col11": None
            })[STANDARD_COLUMNS]

            df_2002 = pd.DataFrame({
                "Code": 2002, "Line_ObjectID": billing_merged["OBJECTID_x"],
                "Trans_Numb": billing_merged["Trans_numb"], "AcctNumber": billing_merged["AcctNumber"],
                "Phase_Code": billing_merged["Phase_Code"], "Col6": 0,
                "X": billing_merged["X"], "Y": billing_merged["Y"],
                "ConsType_Label": billing_merged["ConsType_Label"], "Trans_KVA": None, "Col11": 0
            })[STANDARD_COLUMNS]

            col5_calc = billing_merged["ConsKWH"] / (720 * 0.7 * 0.9)
            df_2004 = pd.DataFrame({
                "Code": 2004, "Line_ObjectID": billing_merged["OBJECTID_x"],
                "Trans_Numb": billing_merged["Trans_numb"], "AcctNumber": billing_merged["AcctNumber"],
                "Phase_Code": col5_calc, "Col6": 90, "X": 1, "Y": 1,
                "ConsType_Label": billing_merged["ConsKWH"], "Trans_KVA": None, "Col11": None
            })[STANDARD_COLUMNS]

            df_2010 = pd.DataFrame({
                "Code": 2010, "Line_ObjectID": base_merged["OBJECTID_x"],
                "Trans_Numb": base_merged["Trans_numb"], "AcctNumber": None,
                "Phase_Code": "Yg", "Col6": "Yg", "X": None, "Y": None,
                "ConsType_Label": None, "Trans_KVA": base_merged["Trans_KVA"], "Col11": None
            })[STANDARD_COLUMNS]

            master_df = pd.concat([df_2001, df_2002, df_2004, df_2010], ignore_index=True)

            # Store results
            self.processed_dfs = {
                "2001": df_2001,
                "2002": df_2002,
                "2004": df_2004,
                "2010": df_2010,
                "master": master_df
            }

            # Enable export buttons
            self.btn_export_individual.config(state="normal")
            self.btn_export_merged.config(state="normal")

            self.status_var.set("Processing complete! Ready to export.")
            messagebox.showinfo("Success", "Data processed successfully!")

        except Exception as e:
            self.status_var.set("Error during processing.")
            messagebox.showerror("Error", f"Failed to process files:\n{str(e)}")

    def export_individual(self):
        target_dir = filedialog.askdirectory(title="Select Folder to Save CSV Files")
        if target_dir:
            for code in ["2001", "2002", "2004", "2010"]:
                file_path = os.path.join(target_dir, f"{code}.csv")
                self.processed_dfs[code].to_csv(file_path, index=False)
            messagebox.showinfo("Success", f"Saved all 4 CSV files to:\n{target_dir}")

    def export_merged(self):
        file_path = filedialog.asksaveasfilename(
            title="Save Merged CSV As",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile="all_merged.csv"
        )
        if file_path:
            self.processed_dfs["master"].to_csv(file_path, index=False)
            messagebox.showinfo("Success", f"Saved master merged file to:\n{file_path}")

# --- Run Application ---
if __name__ == "__main__":
    root = tk.Tk()
    app = FeederDataApp(root)
    root.mainloop()