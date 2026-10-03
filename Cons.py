import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

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

# Function to process pole numbers
def calculate_consumption():
    if df is None:
        messagebox.showerror("Error", "Please load an Excel file first.")
        return
    
    poles = entry_poles.get().split(",")
    poles = [p.strip() for p in poles if p.strip()]
    
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
root.title("Pole Consumption Calculator")
root.geometry("600x400")

df = None

# File load button
btn_load = tk.Button(root, text="Load Excel File", command=load_file)
btn_load.pack(pady=10)

# Pole input
frame_input = tk.Frame(root)
frame_input.pack(pady=10)

tk.Label(frame_input, text="Enter Pole Numbers (comma-separated):").pack(side="left")
entry_poles = tk.Entry(frame_input, width=40)
entry_poles.pack(side="left")

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