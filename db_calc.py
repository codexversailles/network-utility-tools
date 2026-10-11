import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import math

# Capacities
CHEST_CAPACITY = 54 * 64   # 3456 items
SHULKER_CAPACITY = 27 * 64 # 1728 items
STACK_SIZE = 64            # Standard stack size

def calculate_storage():
    # Open file dialog
    file_path = filedialog.askopenfilename(
        title="Select Litematica Material List CSV",
        filetypes=[("CSV files", "*.csv")]
    )
    
    if not file_path:
        return
    
    try:
        # Read CSV
        df = pd.read_csv(file_path)
        
        if "Item" not in df.columns or "Total" not in df.columns:
            messagebox.showerror("Error", "CSV must contain 'Item' and 'Total' columns.")
            return
        # Calculate storage requirements
        df["Double Chests (float)"] = df["Total"] / CHEST_CAPACITY
        df["Shulker Boxes (float)"] = df["Total"] / SHULKER_CAPACITY
        
        # Calculate stacks and leftovers
        df["Stacks"] = df["Total"].apply(
            lambda total: f"{total // STACK_SIZE} stacks & {total % STACK_SIZE} items"
        )
        
        # Totals
        total_items = df["Total"].sum()
        total_chests = total_items / CHEST_CAPACITY
        total_chests_ceil = math.ceil(total_chests)
        total_shulkers = total_items / SHULKER_CAPACITY
        total_shulkers_ceil = math.ceil(total_shulkers)
        
        # Clear old table
        for row in tree.get_children():
            tree.delete(row)
        
        # Insert into table
        for _, row in df.iterrows():
            tree.insert("", tk.END, values=(
                row["Item"],
                row["Total"],
                row["Stacks"],
                f"{row['Double Chests (float)']:.3f}",
                f"{row['Shulker Boxes (float)']:.3f}"
            ))
        
        # Show totals
        result_label.config(
            text=f"Total Items: {total_items}\n"
                 f"Total Double Chests (float): {total_chests:.3f} → Rounded: {total_chests_ceil}\n"
                 f"Total Shulker Boxes (float): {total_shulkers:.3f} → Rounded: {total_shulkers_ceil}"
        )
    
    except Exception as e:
        messagebox.showerror("Error", f"Failed to process file:\n{e}")


# Tkinter setup
root = tk.Tk()
root.title("Minecraft Storage Calculator")
root.geometry("1050x500")

# Button
btn = tk.Button(root, text="Load CSV", command=calculate_storage)
btn.pack(pady=10)

# Table (Treeview)
columns = ("Item", "Total", "Stacks", "Double Chests (float)", "Shulker Boxes (float)")
tree = ttk.Treeview(root, columns=columns, show="headings", height=15)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=200)
tree.pack(fill="both", expand=True)

# Result Label
result_label = tk.Label(root, text="", font=("Arial", 12), justify="left")
result_label.pack(pady=10)

root.mainloop()
