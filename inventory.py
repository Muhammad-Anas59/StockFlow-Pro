# inventory.py
import customtkinter as ctk
import session
from tkinter import messagebox
import tkinter.ttk as ttk
from database import (
    add_product, get_all_products,
    search_products, update_product, delete_product
)

def show_inventory(root_callback):
    win = ctk.CTk()
    win.iconbitmap("icon.ico")
    win.title("StockFlow Pro — Inventory")
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

    nav_btn("Dashboard", "🏠", go_dashboard)
    nav_btn("Inventory", "📋", lambda: None)

    def go_sales():
        win.destroy()
        from sales import show_sales
        show_sales(root_callback)

    nav_btn("Sales", "💰", go_sales)

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
        topbar, text="Inventory Management",
        font=ctk.CTkFont("Arial", 18, "bold"), text_color="white"
    ).pack(side="left", padx=25, pady=15)
    ctk.CTkLabel(topbar, text=f"👤 {session.current_user}", font=ctk.CTkFont("Arial", 12), text_color="#94a3b8").pack(side="right", padx=25)

    # ── FORM + TABLE AREA ──
    body = ctk.CTkFrame(main, fg_color="#0f172a", corner_radius=0)
    body.pack(fill="both", expand=True, padx=20, pady=15)

    # LEFT — Form
    form_frame = ctk.CTkFrame(body, fg_color="#1e293b", corner_radius=12, width=290)
    form_frame.pack(side="left", fill="y", padx=(0, 15))
    form_frame.pack_propagate(False)

    ctk.CTkLabel(
        form_frame, text="Product Details",
        font=ctk.CTkFont("Arial", 14, "bold"), text_color="#38bdf8"
    ).pack(anchor="w", padx=20, pady=(18, 4))

    lbl_editing = ctk.CTkLabel(
        form_frame, text="No product selected — click a row to edit",
        font=ctk.CTkFont("Arial", 10), text_color="#64748b"
    )
    lbl_editing.pack(anchor="w", padx=20, pady=(0, 4))

    fields = {}
    field_list = [
        ("Product Name", "name"),
        ("Category", "category"),
        ("Quantity", "quantity"),
        ("Price (Rs)", "price"),
        ("Supplier", "supplier"),
    ]

    for label, key in field_list:
        ctk.CTkLabel(form_frame, text=label, font=ctk.CTkFont("Arial", 11, "bold"), text_color="#cbd5e1").pack(anchor="w", padx=20)
        entry = ctk.CTkEntry(form_frame, width=240, height=36, placeholder_text=f"Enter {label.lower()}", corner_radius=7)
        entry.pack(padx=20, pady=(2, 6))
        fields[key] = entry

    selected_id = [None]

    def clear_form():
        for e in fields.values():
            e.delete(0, "end")
        selected_id[0] = None
        lbl_editing.configure(text="No product selected — click a row to edit", text_color="#64748b")

    def refresh_table(data=None):
        for row in tree.get_children():
            tree.delete(row)
        rows = data if data is not None else get_all_products()
        for p in rows:
            tree.insert("", "end", values=p)

    def do_add():
        n = fields["name"].get().strip()
        c = fields["category"].get().strip()
        q = fields["quantity"].get().strip()
        p = fields["price"].get().strip()
        s = fields["supplier"].get().strip()
        if not n or not q or not p:
            messagebox.showwarning("Warning", "Name, Quantity and Price are required.", parent=win)
            return
        try:
            float(p); int(q)
        except ValueError:
            messagebox.showerror("Error", "Quantity must be integer, Price must be number.", parent=win)
            return
        add_product(n, c, int(q), float(p), s)
        messagebox.showinfo("Success", "Product added successfully!", parent=win)
        clear_form()
        refresh_table()

    def do_update():
        if not selected_id[0]:
            messagebox.showwarning("Warning", "Select a product from table first.", parent=win)
            return
        n = fields["name"].get().strip()
        c = fields["category"].get().strip()
        q = fields["quantity"].get().strip()
        p = fields["price"].get().strip()
        s = fields["supplier"].get().strip()
        if not n or not q or not p:
            messagebox.showwarning("Warning", "Name, Quantity and Price are required.", parent=win)
            return
        update_product(selected_id[0], n, c, int(q), float(p), s)
        messagebox.showinfo("Success", "Product updated!", parent=win)
        clear_form()
        refresh_table()

    def do_delete():
        if not selected_id[0]:
            messagebox.showwarning("Warning", "Select a product to delete.", parent=win)
            return
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this product?", parent=win):
            delete_product(selected_id[0])
            messagebox.showinfo("Deleted", "Product deleted.", parent=win)
            clear_form()
            refresh_table()

    btn_configs = [
        ("➕  Add Product", "#38bdf8", "#0ea5e9", do_add),
        ("✏️  Update", "#34d399", "#10b981", do_update),
        ("🗑️  Delete", "#ef4444", "#dc2626", do_delete),
        ("🔄  Clear", "#475569", "#334155", clear_form),
    ]

    for text, fg, hover, cmd in btn_configs:
        ctk.CTkButton(
            form_frame, text=text, width=240, height=38,
            fg_color=fg, hover_color=hover,
            text_color="#0f172a" if fg != "#475569" else "white",
            font=ctk.CTkFont("Arial", 12, "bold"),
            corner_radius=8, command=cmd
        ).pack(padx=20, pady=2)

    # RIGHT — Table
    right_frame = ctk.CTkFrame(body, fg_color="#1e293b", corner_radius=12)
    right_frame.pack(side="right", fill="both", expand=True)

    # Search bar
    search_bar = ctk.CTkFrame(right_frame, fg_color="transparent")
    search_bar.pack(fill="x", padx=20, pady=(15, 10))

    ctk.CTkLabel(search_bar, text="🔍", font=("Arial", 16)).pack(side="left")
    txt_search = ctk.CTkEntry(search_bar, width=280, height=36, placeholder_text="Search products...", corner_radius=7)
    txt_search.pack(side="left", padx=8)

    def do_search():
        kw = txt_search.get().strip()
        if kw:
            refresh_table(search_products(kw))
        else:
            refresh_table()

    ctk.CTkButton(
        search_bar, text="Search", width=90, height=36,
        fg_color="#38bdf8", hover_color="#0ea5e9",
        text_color="#0f172a", font=ctk.CTkFont("Arial", 12, "bold"),
        corner_radius=7, command=do_search
    ).pack(side="left")

    ctk.CTkButton(
        search_bar, text="Show All", width=90, height=36,
        fg_color="#38bdf8", hover_color="#0ea5e9",
        text_color="white", font=ctk.CTkFont("Arial", 12, "bold"),
        corner_radius=7, command=lambda: refresh_table()
    ).pack(side="left", padx=8)

    # Treeview table
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

    cols = ("ID", "Name", "Category", "Qty", "Price", "Supplier", "Date")
    tree = ttk.Treeview(right_frame, columns=cols, show="headings", height=15)
    widths = [45, 160, 110, 60, 90, 130, 110]
    for col, w in zip(cols, widths):
        tree.heading(col, text=col)
        tree.column(col, width=w, anchor="center")
    tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def on_row_select(event):
        selected = tree.selection()
        if not selected:
            return
        row = tree.item(selected[0])["values"]
        if not row:
            return
        clear_form()
        selected_id[0] = row[0]
        fields["name"].insert(0, str(row[1]))
        fields["category"].insert(0, str(row[2]))
        fields["quantity"].insert(0, str(row[3]))
        fields["price"].insert(0, str(row[4]))
        fields["supplier"].insert(0, str(row[5]))
        lbl_editing.configure(text=f"✏️ Editing: {row[1]} (ID: {row[0]})", text_color="#34d399")

    tree.bind("<<TreeviewSelect>>", on_row_select)
    refresh_table()
    win.mainloop()