import ipaddress
import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Helper to convert IP to binary dotted form
def ip_to_bin(ip):
    return ".".join(f"{int(octet):08b}" for octet in ip.split("."))

# Function to calculate prefix from host count
def hosts_to_prefix(hosts):
    n = 0
    while (2 ** n) - 2 < hosts:
        n += 1
    return 32 - n

# VLSM calculation
def calculate_vlsm(base_network, host_dict):
    vlsm_data = []
    net = ipaddress.ip_network(base_network, strict=False)
    current = net.network_address
    sorted_hosts = sorted(host_dict.items(), key=lambda x: x[1], reverse=True)

    for name, hosts in sorted_hosts:
        prefix = hosts_to_prefix(hosts)
        subnet = ipaddress.ip_network(f"{current}/{prefix}", strict=False)
        usable_hosts = subnet.num_addresses - 2
        host_range = f"{list(subnet.hosts())[0]} - {list(subnet.hosts())[-1]}"
        broadcast = subnet.broadcast_address
        vlsm_data.append({
            "Network": name,
            "Subnet Address (Decimal)": f"{subnet.network_address}/{prefix}",
            "Subnet Address (Binary)": ip_to_bin(str(subnet.network_address)),
            "Host Address Range (Decimal)": host_range,
            "Broadcast Address (Decimal)": str(broadcast),
            "Broadcast Address (Binary)": ip_to_bin(str(broadcast)),
            "Usable Hosts": usable_hosts
        })
        current = list(subnet.hosts())[-1] + 2
    return vlsm_data

# Non-VLSM (/28 fixed)
def calculate_nonvlsm(base_network, host_dict):
    nonvlsm_data = []
    net = ipaddress.ip_network(base_network, strict=False)
    subnets = list(net.subnets(prefixlen_diff=4))
    for (name, _), subnet in zip(host_dict.items(), subnets):
        usable_hosts = subnet.num_addresses - 2
        host_range = f"{list(subnet.hosts())[0]} - {list(subnet.hosts())[-1]}"
        broadcast = subnet.broadcast_address
        nonvlsm_data.append({
            "Network": name,
            "Subnet Address (Decimal)": f"{subnet.network_address}/28",
            "Subnet Address (Binary)": ip_to_bin(str(subnet.network_address)),
            "Host Address Range (Decimal)": host_range,
            "Broadcast Address (Decimal)": str(broadcast),
            "Broadcast Address (Binary)": ip_to_bin(str(broadcast)),
            "Usable Hosts": usable_hosts
        })
    return nonvlsm_data

# CSV Export
def export_csv(vlsm_data, nonvlsm_data, filename):
    with open(filename, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["VLSM Addressing Scheme"])
        writer.writerow(vlsm_data[0].keys())
        for row in vlsm_data:
            writer.writerow(row.values())
        writer.writerow([])
        writer.writerow(["Non-VLSM Addressing Scheme"])
        writer.writerow(nonvlsm_data[0].keys())
        for row in nonvlsm_data:
            writer.writerow(row.values())

# Main calculation + export
def calculate_and_save():
    try:
        base_network = base_entry.get().strip()
        hosts_input = hosts_text.get("1.0", "end-1c").strip().split("\n")
        host_dict = {}

        for line in hosts_input:
            if line:
                parts = line.split(",")
                name = parts[0].strip()
                count = int(parts[1].strip())
                host_dict[name] = count

        vlsm_data = calculate_vlsm(base_network, host_dict)
        nonvlsm_data = calculate_nonvlsm(base_network, host_dict)

        save_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV files", "*.csv")],
                                                 title="Save CSV File")
        if save_path:
            export_csv(vlsm_data, nonvlsm_data, save_path)
            messagebox.showinfo("Success", f"✅ CSV file generated successfully!\n\nSaved to:\n{save_path}")

    except Exception as e:
        messagebox.showerror("Error", f"⚠️ Something went wrong:\n{e}")

# ---------------- UI ----------------
root = tk.Tk()
root.title("VLSM & Non-VLSM Subnet Calculator")
root.geometry("750x600")
root.resizable(False, False)

# Style
style = ttk.Style(root)
style.configure("TLabel", font=("Segoe UI", 11))
style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=6)
style.configure("TFrame", background="#f9f9f9")

main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill="both", expand=True)

# Header
title_label = ttk.Label(main_frame, text="VLSM & Non-VLSM Subnet Calculator", font=("Segoe UI", 16, "bold"))
title_label.pack(pady=10)

# Base network input
ttk.Label(main_frame, text="Base Network (e.g. 192.168.10.0/24):").pack(anchor="w", pady=(15, 3))
base_entry = ttk.Entry(main_frame, width=40, font=("Consolas", 11))
base_entry.insert(0, "192.168.10.0/24")
base_entry.pack(anchor="w", padx=10)

# Host input text area
ttk.Label(main_frame, text="Enter Networks (Name, Hosts) one per line:").pack(anchor="w", pady=(15, 3))
text_frame = ttk.Frame(main_frame)
text_frame.pack(fill="x")

hosts_scroll = ttk.Scrollbar(text_frame)
hosts_scroll.pack(side="right", fill="y")

hosts_text = tk.Text(text_frame, height=14, width=70, font=("Consolas", 10), yscrollcommand=hosts_scroll.set, wrap="none")
hosts_text.pack()
hosts_scroll.config(command=hosts_text.yview)

hosts_text.insert("1.0", 
"Audio Visual Room, 43\n"
"Library, 24\n"
"Cookery Room, 20\n"
"Faculty Office, 15\n"
"Cashier's Office, 14\n"
"Registrar's Office, 11\n"
"F and B Room, 10\n"
"Campus Ministry, 8\n"
"Principal's Office, 3\n"
"Clinic Office, 2\n"
"Router5↔Router4, 2\n"
"Router5↔Router3, 2"
)

# Button
ttk.Button(main_frame, text="📁 Generate CSV", command=calculate_and_save).pack(pady=20)

# Footer
ttk.Label(main_frame, text="© 2025 Subnet Calculator | Developed by Lance", font=("Segoe UI", 9), foreground="gray").pack(pady=5)

root.mainloop()
