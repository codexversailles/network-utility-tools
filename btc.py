import tkinter as tk

def calculate_profit():
    try:
        investment = float(investment_var.get())
        buy_price = float(buy_price_var.get())
        current_price = float(current_price_var.get())
        target_profit = float(target_profit_var.get())
        exchange_rate = float(exchange_rate_var.get())

        btc_amount = investment / buy_price
        current_value_php = btc_amount * current_price
        profit_php = current_value_php - investment
        profit_percent = (profit_php / investment) * 100
        target_value_php = investment + target_profit
        required_btc_price = target_value_php / btc_amount
        current_value_usd = current_value_php / exchange_rate

        btc_amount_label.config(text=f"{btc_amount:.8f} BTC")
        current_value_label.config(text=f"₱{current_value_php:,.2f}")
        profit_label.config(
            text=f"₱{profit_php:,.2f}  ({profit_percent:.2f}%)",
            fg="#43a047" if profit_php >= 0 else "#e53935"
        )
        required_price_label.config(text=f"₱{required_btc_price:,.2f}")
        current_usd_label.config(text=f"${current_value_usd:,.2f}")

    except ValueError:
        pass


root = tk.Tk()
root.title("₿ BTC Profit Calculator")
root.geometry("820x500")
root.configure(bg="#f0f2f5")

# --- Top Bar (Logo + Title Left-Aligned) ---
top_bar = tk.Frame(root, bg="#f0f2f5")
top_bar.pack(fill="x", pady=(10, 0), padx=20)

# Bitcoin logo (pulsing gold)
logo_label = tk.Label(top_bar, text="₿", font=("Segoe UI", 24, "bold"), fg="#f5b342", bg="#f0f2f5")
logo_label.pack(side="left")

title_label = tk.Label(
    top_bar,
    text="Bitcoin Profit Calculator",
    font=("Segoe UI", 18, "bold"),
    fg="#222222",
    bg="#f0f2f5",
)
title_label.pack(side="left", padx=10)

# --- Glow animation for logo ---
def pulse_glow():
    # Alternate between two gold tones for the glow effect
    current_color = logo_label.cget("fg")
    new_color = "#ffd65a" if current_color == "#f5b342" else "#f5b342"
    logo_label.config(fg=new_color)
    root.after(800, pulse_glow)  # every 0.8s

pulse_glow()

# --- Main Container ---
content = tk.Frame(root, bg="#f0f2f5")
content.pack(fill="both", expand=True, padx=20, pady=10)

# --- Input Frame ---
input_frame = tk.LabelFrame(
    content,
    text="INPUT DETAILS",
    bg="white",
    padx=20,
    pady=15,
    font=("Segoe UI", 10, "bold"),
    fg="#444444",
    bd=1,
    relief="solid",
)
input_frame.pack(side="left", fill="y", padx=15, pady=10)

# --- Output Frame ---
output_frame = tk.LabelFrame(
    content,
    text="RESULT SUMMARY",
    bg="white",
    padx=20,
    pady=15,
    font=("Segoe UI", 10, "bold"),
    fg="#444444",
    bd=1,
    relief="solid",
)
output_frame.pack(side="right", fill="y", padx=15, pady=10)

# --- Input Helper ---
def make_input(label, var, default=""):
    row = tk.Frame(input_frame, bg="white")
    row.pack(fill="x", pady=8)
    tk.Label(
        row, text=label, bg="white", width=22, anchor="w", font=("Segoe UI", 9), fg="#333333"
    ).pack(side="left")
    entry = tk.Entry(row, textvariable=var, width=15, justify="right", font=("Segoe UI", 9), bg="#fafafa", relief="solid", bd=1)
    entry.pack(side="right")
    if default:
        var.set(default)
    return entry

# --- Output Helper ---
def make_output(label_text):
    row = tk.Frame(output_frame, bg="white")
    row.pack(fill="x", pady=8)
    tk.Label(
        row,
        text=label_text,
        bg="white",
        width=26,
        anchor="w",
        font=("Segoe UI", 9, "bold"),
        fg="#222222",
    ).pack(side="left")
    val = tk.Label(
        row,
        text="—",
        bg="white",
        anchor="e",
        width=25,
        font=("Segoe UI", 9),
        fg="#333333",
    )
    val.pack(side="right")
    return val

# --- Input Variables ---
investment_var = tk.StringVar()
buy_price_var = tk.StringVar()
current_price_var = tk.StringVar()
target_profit_var = tk.StringVar()
exchange_rate_var = tk.StringVar(value="58")

# --- Input Fields ---
make_input("Investment Amount (₱):", investment_var)
make_input("Buy Price per BTC (₱):", buy_price_var)
make_input("Current BTC Price (₱):", current_price_var)
make_input("Target Profit Goal (₱):", target_profit_var)
make_input("Exchange Rate (₱ per USD):", exchange_rate_var)

# --- Calculate Button ---
tk.Button(
    input_frame,
    text="CALCULATE",
    command=calculate_profit,
    bg="#2e7d32",
    fg="white",
    font=("Segoe UI", 10, "bold"),
    relief="flat",
    padx=12,
    pady=8,
    activebackground="#388e3c",
    cursor="hand2",
).pack(pady=20)

# --- Output Labels ---
btc_amount_label = make_output("Total BTC Owned:")
current_value_label = make_output("Current Value of Investment (₱):")
profit_label = make_output("Profit / Loss (₱ and %):")
required_price_label = make_output("Required BTC Price for Target (₱):")
current_usd_label = make_output("Current Value (USD):")

# --- Footer ---
tk.Label(
    root,
    text="Gives you a clear view of your BTC performance — current worth, gain/loss, and your target.",
    font=("Segoe UI", 8),
    bg="#f0f2f5",
    fg="#666666",
    wraplength=700,
    justify="center",
).pack(side="bottom", pady=6)

tk.Label(
    root,
    text="© 2025 Lance — BTC Profit Calculator",
    font=("Segoe UI", 8),
    bg="#f0f2f5",
    fg="#999999",
).pack(side="bottom", pady=2)

root.mainloop()
