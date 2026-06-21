# sales.py
import customtkinter as ctk
import session
from tkinter import messagebox, filedialog
import tkinter.ttk as ttk
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from database import (
    get_products_for_sale, record_sale,
    get_all_sales, get_sales_stats, get_sale_by_id
)

def show_sales(root_callback):
    win = ctk.CTk()
    win.iconbitmap("icon.ico")
    win.title("StockFlow Pro — Sales")
    win.geometry("1100x650")
    win.resizable(False, False)
    ctk.set_appearance_mode("dark")

    win.update_idletasks()
    x = (win.winfo_screenwidth() // 2) - 550
    y = (win.winfo_screenheight() // 2) - 325
    win.geometry(f"1100x650+{x}+{y}")

    def generate_receipt(sale_id, product_name, category, qty, unit_price, total, sale_date):
        file_path = filedialog.asksaveasfilename(
            parent=win,
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"Receipt_{sale_id}.pdf"
        )
        if not file_path:
            return
        try:
            doc = SimpleDocTemplate(file_path, pagesize=letter, topMargin=50, bottomMargin=50)
            styles = getSampleStyleSheet()
            center_title = ParagraphStyle("CenterTitle", parent=styles["Title"], alignment=1)
            center_normal = ParagraphStyle("CenterNormal", parent=styles["Normal"], alignment=1)

            elements = [
                Paragraph("StockFlow Pro", center_title),
                Paragraph("Sales Receipt", center_normal),
                Spacer(1, 14),
                Paragraph(f"Receipt No: #{sale_id}", styles["Normal"]),
                Paragraph(f"Date: {sale_date}", styles["Normal"]),
                Spacer(1, 18),
            ]

            table_data = [
                ["Product", "Category", "Qty", "Unit Price (Rs)", "Total (Rs)"],
                [product_name, category or "-", str(qty), f"{unit_price:,.2f}", f"{total:,.2f}"]
            ]
            t = Table(table_data, colWidths=[120, 100, 50, 110, 100])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ALIGN", (2, 0), (-1, -1), "CENTER"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 24))
            elements.append(Paragraph(f"<b>Total Amount: Rs {total:,.2f}</b>", styles["Normal"]))
            elements.append(Spacer(1, 30))
            elements.append(Paragraph("Thank you for your purchase!", center_normal))

            doc.build(elements)
            messagebox.showinfo("Success", f"Receipt saved to:\n{file_path}", parent=win)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save receipt:\n{e}", parent=win)


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

    def go_settings():
        win.destroy()
        from settings import show_settings
        show_settings(root_callback)

    nav_btn("Settings", "⚙️", go_settings)

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
    product_map = {}  # name -> (id, category, price, stock)
    product_names = []
    for p in products:
        label = f"{p[1]}"
        product_map[label] = {"id": p[0], "category": p[2], "price": float(p[3]), "stock": p[4]}
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
            sale_id = record_sale(info["id"], qty, total)
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
                product_map[label] = {"id": p[0], "category": p[2], "price": float(p[3]), "stock": p[4]}
                product_names.append(label)
            dropdown.configure(values=product_names if product_names else ["No products"])
            if messagebox.askyesno("Print Receipt", "Would you like to print a receipt for this sale?", parent=win):
                generate_receipt(
                    sale_id, name, info.get("category"), qty,
                    info["price"], total, datetime.now().strftime("%Y-%m-%d %H:%M")
                )
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

    def reprint_receipt():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a sale from the table first.", parent=win)
            return
        row = tree.item(selected[0])["values"]
        sale_id = row[0]
        sale_data = get_sale_by_id(sale_id)
        if not sale_data:
            messagebox.showerror("Error", "Sale not found.", parent=win)
            return
        _, p_name, p_category, qty_sold, total_price, sale_date = sale_data
        unit_price = float(total_price) / qty_sold
        generate_receipt(sale_id, p_name, p_category, qty_sold, unit_price, float(total_price), str(sale_date))

    ctk.CTkButton(
        right_frame, text="🧾  Reprint Receipt", width=200, height=38,
        fg_color="#a78bfa", hover_color="#8b5cf6",
        text_color="#0f172a", font=ctk.CTkFont("Arial", 12, "bold"),
        corner_radius=8, command=reprint_receipt
    ).pack(padx=10, pady=(0, 10))

    def refresh_table():
        for row in tree.get_children():
            tree.delete(row)
        for sale in get_all_sales():
            tree.insert("", "end", values=sale)

    refresh_table()
    win.mainloop()