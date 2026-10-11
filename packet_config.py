#!/usr/bin/env python3
"""
Packet Tracer CLI Text Maker (single combined .txt)
Reads a CSV (as produced by the VLSM/Non-VLSM calculator),
lets you assign networks to router interfaces, and generates
a single combined router CLI text file to paste into Packet Tracer.

Author: Lance (Made by Lance watermark in UI)
"""
import csv
import ipaddress
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from collections import defaultdict
from pathlib import Path

APP_TITLE = "Packet Tracer .txt Maker — Made by Lance"

# ----------------- Helpers -----------------
def ip_to_netmask(prefixlen: int) -> str:
    mask = (0xFFFFFFFF << (32 - prefixlen)) & 0xFFFFFFFF
    return ".".join(str((mask >> (i * 8)) & 0xFF) for i in reversed(range(4)))

def first_usable_ip(network: ipaddress.IPv4Network) -> str:
    hosts = list(network.hosts())
    return str(hosts[0]) if hosts else None

def parse_csv_for_networks(path):
    """
    Parse CSV and return list of dicts:
    { "Section": "VLSM"|"NONVLSM"|None, "Network": name, "Subnet": '192.168.10.0/26', ... }
    The CSV format this expects is similar to the earlier exporter:
    - There are section header lines like "VLSM Addressing Scheme" or "Non-VLSM Addressing Scheme"
    - Then a header row containing "Network" and "Subnet Address (Decimal)" or "Subnet Address"
    """
    networks = []
    section = None
    headers = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            first = row[0].strip().lower()
            # Section detection
            if "vlsm" in first:
                section = "VLSM"
                headers = []
                continue
            if "non-vlsm" in first or "nonvlsm" in first:
                section = "NONVLSM"
                headers = []
                continue
            # detect header row
            lowcells = [c.strip().lower() for c in row]
            if "network" in lowcells and any("subnet" in c for c in lowcells):
                headers = [c.strip() for c in row]
                continue
            # parse a data row if headers present
            if headers:
                # pad shorter rows
                if len(row) < len(headers):
                    row = row + [''] * (len(headers) - len(row))
                rec = {headers[i]: row[i].strip() for i in range(len(headers))}
                # Pull Network and Subnet fields (attempt a few common header names)
                netname = rec.get("Network") or rec.get("network") or rec.get(list(rec.keys())[0])
                subnet_field = rec.get("Subnet Address (Decimal)") or rec.get("Subnet Address") or rec.get("Subnet") or rec.get("Subnet Address (Decimal) ")
                # fallback: search any cell for ip/prefix
                subnet = None
                if subnet_field:
                    # Take first token that looks like ip/prefix
                    tok = subnet_field.split()[0].strip().strip(',')
                    if '/' in tok and tok.count('.') == 3:
                        subnet = tok
                if not subnet:
                    for v in rec.values():
                        if "/" in v and v.count(".") == 3:
                            subnet = v.split()[0].strip().strip(',')
                            break
                if netname and subnet:
                    networks.append({
                        "Section": section,
                        "Network": netname,
                        "Subnet": subnet,
                        "RawRow": rec
                    })
                # else ignore malformed row
    return networks

# ----------------- App -----------------
class PacketTxtMaker:
    def __init__(self, root):
        self.root = root
        root.title(APP_TITLE)
        root.geometry("1000x700")
        root.minsize(900, 600)

        # Data
        self.networks = []  # list of parsed network dicts
        self.assignments = defaultdict(list)  # router -> list of assignment dicts
        self.if_counters = defaultdict(int)  # router -> counter for subinterfaces

        # Build UI
        self._build_ui()

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill="both", expand=True)

        # Top controls
        top = ttk.Frame(main)
        top.pack(fill="x", pady=(0, 8))

        btn_load = ttk.Button(top, text="Load CSV", command=self.load_csv)
        btn_load.pack(side="left")

        ttk.Label(top, text="Show Section:").pack(side="left", padx=(12,4))
        self.section_var = tk.StringVar(value="VLSM")
        ttk.Combobox(top, textvariable=self.section_var, values=("VLSM","NONVLSM","ALL"), width=10, state="readonly").pack(side="left")

        ttk.Label(top, text="Router Name:").pack(side="left", padx=(12,4))
        self.router_entry = ttk.Entry(top, width=14)
        self.router_entry.pack(side="left")

        ttk.Label(top, text="Interface base:").pack(side="left", padx=(12,4))
        self.ifbase_entry = ttk.Entry(top, width=22)
        self.ifbase_entry.insert(0, "GigabitEthernet0/0")
        self.ifbase_entry.pack(side="left")

        ttk.Button(top, text="Assign Selected → Router", command=self.assign_selected).pack(side="left", padx=(12,0))
        ttk.Button(top, text="Preview Router CLI", command=self.preview_router_cli).pack(side="left", padx=(8,0))

        # Middle split: left networks, right assignments & preview
        pan = ttk.Panedwindow(main, orient="horizontal")
        pan.pack(fill="both", expand=True)

        # Left: networks Treeview
        left = ttk.Labelframe(pan, text="Detected Networks")
        pan.add(left, weight=2)

        cols = ("Section", "Network", "Subnet")
        self.net_tree = ttk.Treeview(left, columns=cols, show="headings", selectmode="extended")
        for c in cols:
            self.net_tree.heading(c, text=c)
            self.net_tree.column(c, width=160, anchor="w")
        self.net_tree.pack(fill="both", expand=True, side="left")
        net_scroll = ttk.Scrollbar(left, orient="vertical", command=self.net_tree.yview)
        self.net_tree.configure(yscrollcommand=net_scroll.set)
        net_scroll.pack(side="right", fill="y")

        # Right: assignments and CLI preview
        right = ttk.Labelframe(pan, text="Assignments & Preview")
        pan.add(right, weight=1)

        # Assignment controls
        as_ctrl = ttk.Frame(right)
        as_ctrl.pack(fill="x", pady=(4,6))
        ttk.Button(as_ctrl, text="Remove Selected Assignment", command=self.remove_assignment).pack(side="left")
        ttk.Button(as_ctrl, text="Auto-assign sequentially", command=self.autofill_seq).pack(side="left", padx=(6,0))

        # Assignments Treeview
        acols = ("Router","Interface","Subnet","Network")
        self.assign_tree = ttk.Treeview(right, columns=acols, show="headings")
        for c in acols:
            self.assign_tree.heading(c, text=c)
            self.assign_tree.column(c, width=110, anchor="w")
        self.assign_tree.pack(fill="both", expand=True)

        # CLI preview
        ttk.Label(right, text="Router CLI Preview:").pack(anchor="w", pady=(8,0))
        self.preview_text = tk.Text(right, height=12, wrap="none", font=("Consolas", 10))
        self.preview_text.pack(fill="both", expand=False)

        # Bottom controls
        bottom = ttk.Frame(main)
        bottom.pack(fill="x", pady=(8,0))
        ttk.Button(bottom, text="Generate Combined .txt", command=self.generate_combined_txt).pack(side="left")
        ttk.Button(bottom, text="Save Assignments (CSV)", command=self.save_assignments_csv).pack(side="left", padx=(8,0))
        ttk.Button(bottom, text="Clear All", command=self.clear_all).pack(side="left", padx=(8,0))

        # Status and watermark
        status_frame = ttk.Frame(main)
        status_frame.pack(fill="x", pady=(8,0))
        ttk.Label(status_frame, text="Status:").pack(side="left")
        self.status = tk.StringVar(value="Ready")
        ttk.Label(status_frame, textvariable=self.status).pack(side="left", padx=(6,0))

        # Watermark (Made by Lance)
        watermark = tk.Label(self.root, text="Made by Lance", font=("Segoe UI", 10, "italic"), fg="gray70", bg=self.root.cget("bg"))
        watermark.place(relx=1.0, rely=1.0, x=-8, y=-8, anchor="se")

    # ----------------- Actions -----------------
    def load_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files","*.csv"),("All files","*.*")])
        if not path:
            return
        try:
            nets = parse_csv_for_networks(path)
            if not nets:
                messagebox.showerror("No networks found", "CSV parsed but no networks detected. Check format.")
                return
            self.networks = nets
            self.populate_net_tree()
            self.status.set(f"Loaded {len(self.networks)} networks from CSV")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV:\n{e}")

    def populate_net_tree(self):
        for i in self.net_tree.get_children():
            self.net_tree.delete(i)
        show = self.section_var.get()
        for idx, rec in enumerate(self.networks):
            if show != "ALL" and rec.get("Section") != show:
                continue
            self.net_tree.insert("", "end", iid=str(idx), values=(rec.get("Section") or "", rec.get("Network"), rec.get("Subnet")))

    def assign_selected(self):
        sel = self.net_tree.selection()
        if not sel:
            messagebox.showwarning("Select networks", "Select one or more networks to assign.")
            return
        router = self.router_entry.get().strip()
        if not router:
            messagebox.showwarning("Router name", "Enter a Router Name (e.g., Router5).")
            return
        ifbase = self.ifbase_entry.get().strip()
        if not ifbase:
            messagebox.showwarning("Interface base", "Enter an Interface base (e.g., GigabitEthernet0/0).")
            return

        for iid in sel:
            rec = self.networks[int(iid)]
            subnet_s = rec["Subnet"]
            try:
                net = ipaddress.ip_network(subnet_s, strict=False)
            except Exception as e:
                messagebox.showerror("Invalid subnet", f"Could not parse subnet '{subnet_s}': {e}")
                continue
            # generate interface name / increment counter
            idx = self.if_counters[router]
            ifname = f"{ifbase}.{idx}"  # use subinterface form
            self.if_counters[router] += 1

            gw = first_usable_ip(net)
            mask = ip_to_netmask(net.prefixlen)
            assign = {
                "Router": router,
                "Interface": ifname,
                "Subnet": str(net.with_prefixlen),
                "NetworkName": rec["Network"],
                "Gateway": gw,
                "Mask": mask
            }
            # store and display
            self.assignments[router].append(assign)
            self.assign_tree.insert("", "end", values=(router, ifname, assign["Subnet"], assign["NetworkName"]))
            # remove from network list to prevent double assign
            self.net_tree.delete(iid)

        self.status.set(f"Assigned {len(sel)} networks to {router}")

    def remove_assignment(self):
        sel = self.assign_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select assignment(s) to remove.")
            return
        for iid in sel:
            vals = self.assign_tree.item(iid, "values")
            router, ifname, subnet, network = vals
            # remove from assignments
            lst = self.assignments.get(router, [])
            for e in lst:
                if e["Interface"] == ifname and e["Subnet"] == subnet:
                    lst.remove(e)
                    break
            self.assign_tree.delete(iid)
        self.status.set("Removed selected assignment(s)")

    def autofill_seq(self):
        # simple sequential auto assign: pick visible items and assign round-robin to routers specified in router_entry (comma separated),
        items = self.net_tree.get_children()
        if not items:
            messagebox.showinfo("Nothing to assign", "No networks to auto-assign.")
            return
        routers = [r.strip() for r in self.router_entry.get().split(",") if r.strip()]
        if not routers:
            routers = ["Router5", "Router4", "Router3"]
        base = self.ifbase_entry.get().strip() or "GigabitEthernet0/0"
        ridx = 0
        for iid in list(items):
            chosen = routers[ridx % len(routers)]
            self.router_entry.delete(0, "end"); self.router_entry.insert(0, chosen)
            self.ifbase_entry.delete(0, "end"); self.ifbase_entry.insert(0, base)
            self.net_tree.selection_set(iid)
            self.assign_selected()
            ridx += 1
        self.status.set("Auto-assigned networks sequentially")

    def preview_router_cli(self):
        sel = self.assign_tree.selection()
        if not sel:
            messagebox.showwarning("Select assignment", "Select an assignment row to preview that router's CLI.")
            return
        # take first selected and find its router
        vals = self.assign_tree.item(sel[0], "values")
        router = vals[0]
        # build CLI for that router
        entries = self.assignments.get(router, [])
        if not entries:
            messagebox.showinfo("No entries", f"No assignments found for {router}.")
            return
        cli = self._build_router_block(router, entries)
        self.preview_text.delete("1.0", "end")
        self.preview_text.insert("1.0", cli)

    def _build_router_block(self, router, entries):
        lines = []
        lines.append(f"!\nhostname {router}\n!")
        for e in entries:
            lines.append(f"\n! Interface for {e['NetworkName']} ({e['Subnet']})")
            lines.append(f"interface {e['Interface']}")
            lines.append(f" description Connected to {e['NetworkName']}")
            lines.append(f" ip address {e['Gateway']} {e['Mask']}")
            lines.append(" no shutdown")
        lines.append("\n!\n")
        return "\n".join(lines)

    def generate_combined_txt(self):
        if not self.assignments:
            messagebox.showwarning("No assignments", "Assign networks to routers first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files","*.txt")])
        if not path:
            return
        try:
            all_blocks = []
            for router, entries in self.assignments.items():
                all_blocks.append(self._build_router_block(router, entries))
            content = "\n".join(all_blocks)
            Path(path).write_text(content, encoding='utf-8')
            messagebox.showinfo("Saved", f"Combined config saved to:\n{path}\n\nCopy/paste each router block into Packet Tracer CLI.")
            self.status.set(f"Saved combined config: {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{e}")

    def save_assignments_csv(self):
        # optional: export a CSV of current assignments
        if not self.assignments:
            messagebox.showwarning("No assignments", "No assignments to save.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
        if not path:
            return
        try:
            rows = []
            for router, entries in self.assignments.items():
                for e in entries:
                    rows.append([router, e["Interface"], e["Subnet"], e["NetworkName"], e["Gateway"], e["Mask"]])
            with open(path, "w", newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Router","Interface","Subnet","NetworkName","Gateway","Mask"])
                writer.writerows(rows)
            messagebox.showinfo("Saved", f"Assignments CSV saved to:\n{path}")
            self.status.set(f"Assignments CSV saved: {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save assignments CSV:\n{e}")

    def clear_all(self):
        if not messagebox.askyesno("Confirm", "Clear all loaded networks and assignments?"):
            return
        self.networks.clear()
        self.assignments.clear()
        self.if_counters.clear()
        for i in self.net_tree.get_children():
            self.net_tree.delete(i)
        for i in self.assign_tree.get_children():
            self.assign_tree.delete(i)
        self.preview_text.delete("1.0", "end")
        self.status.set("Cleared")

# ----------------- Run -----------------
def main():
    root = tk.Tk()
    # Use default ttk theme; could customize fonts/styles here
    app = PacketTxtMaker(root)
    root.mainloop()

if __name__ == "__main__":
    main()
