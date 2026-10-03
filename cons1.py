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
    
    # Get text from Text widget and split by lines
    poles = entry_poles.get("1.0", tk.END).splitlines()
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
    
    # Insert new results with count column
    for i, (_, row) in enumerate(filtered.iterrows(), start=1):
        tree.insert("", "end", values=(i, row["PoleNo"], row["AcctName"], row["ConsKWH"]))
    
    total = filtered["ConsKWH"].sum()
    lbl_total.config(text=f"Total Consumption: {total} kWh")
    lbl_count.config(text=f"Records Found: {len(filtered)}")

# Main window
root = tk.Tk()
root.title("Pole Consumption Calculator")
root.geometry("700x500")

df = None

# File load button
btn_load = tk.Button(root, text="Load Excel File", command=load_file)
btn_load.pack(pady=10)

# Pole input
frame_input = tk.Frame(root)
frame_input.pack(pady=10, fill="x")

tk.Label(frame_input, text="Enter Pole Numbers (one per line):").pack(anchor="w")

# Use Text widget instead of Entry
entry_poles = tk.Text(frame_input, width=50, height=12)
entry_poles.pack()

btn_calc = tk.Button(root, text="Calculate", command=calculate_consumption)
btn_calc.pack(pady=10)

# Results table with Count column
columns = ("Count", "PoleNo", "AcctName", "ConsKWH")
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
tree.pack(expand=True, fill="both")

# Labels for totals
lbl_total = tk.Label(root, text="Total Consumption: 0 kWh", font=("Arial", 12, "bold"))
lbl_total.pack(pady=5)

lbl_count = tk.Label(root, text="Records Found: 0", font=("Arial", 12, "bold"))
lbl_count.pack(pady=5)

root.mainloop()