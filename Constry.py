import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import re

df = None

# Function to load Excel file
def load_file():
    file_path = filedialog.askopenfilename(
        title="Select Excel File",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )
    if file_path:
        global df
        try:
            df = pd.read_excel(file_path)
            messagebox.showinfo("Success", "File loaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file:\n{e}")

# Function to normalize pole numbers (strip suffixes like -S1, -T1, etc.)
def normalize_pole(pole):
    # Keep only the base pattern: digits-digits
    match = re.match(r"^\d+-\d+", pole)
    return match.group(0) if match else pole

# Function to process pole numbers
def calculate_consumption():
    if df is None:
        messagebox.showerror("Error", "Please load an Excel file first.")
        return
    
    poles_raw = text_input.get("1.0", tk.END).splitlines()
    poles = [normalize_pole(p.strip()) for p in poles_raw if p.strip()]
    
    if not poles:
        messagebox.showerror("Error", "Please enter pole numbers.")
        return
    
    filtered = df[df["PoleNo"].isin(poles)]
    
    if filtered.empty:
        messagebox.showinfo("Result", "No matching records found.")
        return
    
    # Clear previous results
    for row in tree.get_children():
        tree.delete(row)
    
    # Insert new results
    for _, row in filtered.iterrows():
        tree.insert("", "end", values=(row["PoleNo"], row["AcctName"], row["ConsKWH"]))
    
    total = filtered["ConsKWH"].sum()
    lbl_total.config(text=f"Total Consumption: {total} kWh")

# Main window
root = tk.Tk()
root.title("GIS Pole Consumption Calculator")
root.geometry("700x500")

# File load button
btn_load = tk.Button(root, text="Load Excel File", command=load_file)
btn_load.pack(pady=10)

# Pole input (multi-line text box for easy pasting from GIS)
tk.Label(root, text="Paste Pole Numbers (one per line):").pack()
text_input = tk.Text(root, height=10, width=60)
text_input.pack(pady=10)

btn_calc = tk.Button(root, text="Calculate", command=calculate_consumption)
btn_calc.pack(pady=10)

# Results table
columns = ("PoleNo", "AcctName", "ConsKWH")
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
tree.pack(expand=True, fill="both")

# Total label
lbl_total = tk.Label(root, text="Total Consumption: 0 kWh", font=("Arial", 12, "bold"))
lbl_total.pack(pady=10)

root.mainloop()