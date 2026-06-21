# sales.py
import customtkinter as ctk
import session
from tkinter import messagebox
import tkinter.ttk as ttk
from database import (
    get_products_for_sale, record_sale,
    get_all_sales, get_sales_stats
)

def show_sales(root_callback):
    win = ctk.CTk()
    win.title("StockFlow Pro — Sales")
    win.geometry("1100x650")
    win.resizable(False, False)
    ctk.set_appearance_mode("dark")

    win.update_idletasks()
    x = (win.winfo_screenwidth() // 2) - 550
    y = (win.winfo_screenheight() // 2) - 325
    win.geometry(f"1100x650+{x}+{y}")

    # ── SIDEBAR ──
    sidebar = ctk.CTkFrame(win, width=220, fg_color="#0f172a", corner_radius=0)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    ctk.CTkLabel(sidebar, text="📦", font=("Arial", 40)).pack(pady=(30, 2))
    ctk.CTkLabel(
        sidebar, text="StockFlow Pro",
        font=ctk.CTkFont("Arial", 16, "bold"),
        text_color="#38bdf8"
    ).pack()
    ctk.CTkLabel(sidebar, text="─" * 22, text_color="#1e293b").pack(pady=(15, 10))

    def nav_btn(text, icon, cmd):
        ctk.CTkButton(
            sidebar, text=f"  {icon}  {text}",
            fg_color="transparent", hover_color="#1e293b",
            anchor="w", font=ctk.CTkFont("Arial", 13),
            text_color="#94a3b8", height=42, command=cmd
        ).pack(fill="x", padx=10, pady=2)

    def go_dashboard():
        win.destroy()
        from dashboard import show_dashboard
        show_dashboard(root_callback)

    def go_inventory():
        win.destroy()
        from inventory import show_inventory
        show_inventory(root_callback)

    nav_btn("Dashboard", "🏠", go_dashboard)
    nav_btn("Inventory", "📋", go_inventory)
    nav_btn("Sales", "💰", lambda: None)

    def go_reports():
        win.destroy()
        from reports import show_reports
        show_reports(root_callback)

    nav_btn("Reports", "📊", go_reports)
    nav_btn("Settings", "⚙️", lambda: None)

    def do_logout():
        win.destroy()
        from login import show_login
        show_login(root_callback)

    ctk.CTkButton(
        sidebar, text="  🚪  Logout",
        fg_color="transparent", hover_color="#1e293b",
        anchor="w", font=ctk.CTkFont("Arial", 13),
        text_color="#ef4444", height=42, command=do_logout
    ).pack(fill="x", padx=10, pady=2, side="bottom")

    # ── MAIN CONTENT ──
    main = ctk.CTkFrame(win, fg_color="#0f172a", corner_radius=0)
    main.pack(side="right", fill="both", expand=True)

    # Topbar
    topbar = ctk.CTkFrame(main, fg_color="#1e293b", height=60, corner_radius=0)
    topbar.pack(fill="x")
    topbar.pack_propagate(False)
    ctk.CTkLabel(
        topbar, text="Sales Management",
        font=ctk.CTkFont("Arial", 18, "bold"),
        text_color="white"
    ).pack(side="left", padx=25, pady=15)
    ctk.CTkLabel(topbar, text=f"👤 {session.current_user}", font=ctk.CTkFont("Arial", 12), text_color="#94a3b8").pack(side="right", padx=25)

    # ── STATS ROW ──
    stats_frame = ctk.CTkFrame(main, fg_color="transparent")
    stats_frame.pack(fill="x", padx=20, pady=(15, 5))

    stats = get_sales_stats()
    cards = [
        ("🧾", "Total Sales", str(stats[0]), "#38bdf8"),
        ("💰", "Total Revenue", f"Rs {stats[1]:,}", "#34d399"),
        ("📦", "Items Sold", str(stats[2]), "#a78bfa"),
    ]
    for icon, title, value, color in cards:
        card = ctk.CTkFrame(stats_frame, fg_color="#1e293b", corner_radius=12, width=200, height=90)
        card.pack(side="left", padx=(0, 15))
        card.pack_propagate(False)
        ctk.CTkLabel(card, text=f"{icon}  {value}", font=ctk.CTkFont("Arial", 20, "bold"), text_color=color).pack(anchor="w", padx=18, pady=(16, 2))
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont("Arial", 11), text_color="#64748b").pack(anchor="w", padx=18)

    # ── BODY ──
    body = ctk.CTkFrame(main, fg_color="#0f172a", corner_radius=0)
    body.pack(fill="both", expand=True, padx=20, pady=10)

    # LEFT — Sale Form
    form_frame = ctk.CTkFrame(body, fg_color="#1e293b", corner_radius=12, width=290)
    form_frame.pack(side="left", fill="y", padx=(0, 15))
    form_frame.pack_propagate(False)

    ctk.CTkLabel(
        form_frame, text="Record a Sale",
        font=ctk.CTkFont("Arial", 14, "bold"),
        text_color="#38bdf8"
    ).pack(anchor="w", padx=20, pady=(18, 10))

    # Product dropdown
    ctk.CTkLabel(form_frame, text="Select Product", font=ctk.CTkFont("Arial", 11, "bold"), text_color="#cbd5e1").pack(anchor="w", padx=20)

    products = get_products_for_sale()
    product_map = {}  # name -> (id, price, stock)
    product_names = []
    for p in products:
        label = f"{p[1]}"
        product_map[label] = {"id": p[0], "price": float(p[2]), "stock": p[3]}
        product_names.append(label)

    selected_product = ctk.StringVar(value=product_names[0] if product_names else "No products available")

    dropdown = ctk.CTkOptionMenu(
        form_frame, values=product_names if product_names else ["No products"],
        variable=selected_product, width=240, height=36,
        fg_color="#0f172a", button_color="#38bdf8",
        button_hover_color="#0ea5e9", corner_radius=7
    )
    dropdown.pack(padx=20, pady=(4, 10))

    # Price display
    ctk.CTkLabel(form_frame, text="Unit Price (Rs)", font=ctk.CTkFont("Arial", 11, "bold"), text_color="#cbd5e1").pack(anchor="w", padx=20)
    lbl_price = ctk.CTkLabel(form_frame, text="—", font=ctk.CTkFont("Arial", 13, "bold"), text_color="#34d399")
    lbl_price.pack(anchor="w", padx=20, pady=(4, 10))

    # Stock display
    ctk.CTkLabel(form_frame, text="Available Stock", font=ctk.CTkFont("Arial", 11, "bold"), text_color="#cbd5e1").pack(anchor="w", padx=20)
    lbl_stock = ctk.CTkLabel(form_frame, text="—", font=ctk.CTkFont("Arial", 13, "bold"), text_color="#f59e0b")
    lbl_stock.pack(anchor="w", padx=20, pady=(4, 10))

    # Quantity
    ctk.CTkLabel(form_frame, text="Quantity to Sell", font=ctk.CTkFont("Arial", 11, "bold"), text_color="#cbd5e1").pack(anchor="w", padx=20)
    txt_qty = ctk.CTkEntry(form_frame, width=240, height=36, placeholder_text="Enter quantity", corner_radius=7)
    txt_qty.pack(padx=20, pady=(4, 10))

    # Total
    ctk.CTkLabel(form_frame, text="Total Amount (Rs)", font=ctk.CTkFont("Arial", 11, "bold"), text_color="#cbd5e1").pack(anchor="w", padx=20)
    lbl_total = ctk.CTkLabel(form_frame, text="—", font=ctk.CTkFont("Arial", 16, "bold"), text_color="#38bdf8")
    lbl_total.pack(anchor="w", padx=20, pady=(4, 15))

    def update_info(*args):
        name = selected_product.get()
        if name in product_map:
            info = product_map[name]
            lbl_price.configure(text=f"Rs {info['price']:,}")
            lbl_stock.configure(text=str(info['stock']))
            calculate_total()

    def calculate_total(*args):
        name = selected_product.get()
        qty = txt_qty.get().strip()
        if name in product_map and qty.isdigit():
            total = product_map[name]["price"] * int(qty)
            lbl_total.configure(text=f"Rs {total:,}")
        else:
            lbl_total.configure(text="—")

    selected_product.trace("w", update_info)
    txt_qty.bind("<KeyRelease>", calculate_total)

    if product_names:
        update_info()

    def do_sale():
        name = selected_product.get()
        qty = txt_qty.get().strip()

        if name not in product_map:
            messagebox.showwarning("Warning", "Please select a valid product.", parent=win)
            return
        if not qty.isdigit() or int(qty) <= 0:
            messagebox.showerror("Error", "Please enter a valid quantity.", parent=win)
            return

        info = product_map[name]
        qty = int(qty)

        if qty > info["stock"]:
            messagebox.showerror("Error", f"Not enough stock! Available: {info['stock']}", parent=win)
            return

        total = info["price"] * qty
        confirm = messagebox.askyesno(
            "Confirm Sale",
            f"Product: {name}\nQuantity: {qty}\nTotal: Rs {total:,}\n\nConfirm sale?",
            parent=win
        )
        if confirm:
            record_sale(info["id"], qty, total)
            messagebox.showinfo("Success", f"Sale recorded!\nRevenue: Rs {total:,}", parent=win)
            txt_qty.delete(0, "end")
            lbl_total.configure(text="—")
            refresh_table()
            # Refresh product list
            new_products = get_products_for_sale()
            product_map.clear()
            product_names.clear()
            for p in new_products:
                label = f"{p[1]}"
                product_map[label] = {"id": p[0], "price": float(p[2]), "stock": p[3]}
                product_names.append(label)
            dropdown.configure(values=product_names if product_names else ["No products"])

    ctk.CTkButton(
        form_frame, text="✅  Record Sale", width=240, height=42,
        fg_color="#34d399", hover_color="#10b981",
        text_color="#0f172a", font=ctk.CTkFont("Arial", 13, "bold"),
        corner_radius=8, command=do_sale
    ).pack(padx=20, pady=4)

    # RIGHT — Sales Table
    right_frame = ctk.CTkFrame(body, fg_color="#1e293b", corner_radius=12)
    right_frame.pack(side="right", fill="both", expand=True)

    ctk.CTkLabel(
        right_frame, text="Sales History",
        font=ctk.CTkFont("Arial", 14, "bold"),
        text_color="#38bdf8"
    ).pack(anchor="w", padx=20, pady=(15, 10))

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview",
        background="#1e293b", foreground="white",
        fieldbackground="#1e293b", rowheight=32,
        font=("Arial", 11)
    )
    style.configure("Treeview.Heading",
        background="#0f172a", foreground="#38bdf8",
        font=("Arial", 11, "bold")
    )
    style.map("Treeview", background=[("selected", "#38bdf8")], foreground=[("selected", "#0f172a")])

    cols = ("ID", "Product", "Category", "Qty Sold", "Total (Rs)", "Date")
    tree = ttk.Treeview(right_frame, columns=cols, show="headings", height=15)
    widths = [45, 180, 120, 80, 110, 160]
    for col, w in zip(cols, widths):
        tree.heading(col, text=col)
        tree.column(col, width=w, anchor="center")
    tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def refresh_table():
        for row in tree.get_children():
            tree.delete(row)
        for sale in get_all_sales():
            tree.insert("", "end", values=sale)

    refresh_table()
    win.mainloop()