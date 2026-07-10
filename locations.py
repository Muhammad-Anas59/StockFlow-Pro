# locations.py
import customtkinter as ctk
import session
from tkinter import messagebox
import tkinter.ttk as ttk
from database import get_connection, add_location

def show_locations(root_callback):
    win = ctk.CTk()
    win.iconbitmap("icon.ico")
    win.title("StockFlow Pro — Locations")
    win.geometry("1100x750")
    win.resizable(False, False)
    ctk.set_appearance_mode("dark")

    win.update_idletasks()
    x = (win.winfo_screenwidth() // 2) - 550
    y = (win.winfo_screenheight() // 2) - 375
    win.geometry(f"1100x750+{x}+{y}")

    # ── SIDEBAR (same pattern as inventory.py) ──
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

    def go_sales():
        win.destroy()
        from sales import show_sales
        show_sales(root_callback)

    def go_reports():
        win.destroy()
        from reports import show_reports
        show_reports(root_callback)

    def go_settings():
        win.destroy()
        from settings import show_settings
        show_settings(root_callback)

    nav_btn("Dashboard", "🏠", go_dashboard)
    nav_btn("Inventory", "📋", go_inventory)
    nav_btn("Sales", "💰", go_sales)
    nav_btn("Locations", "📍", lambda: None)
    nav_btn("Reports", "📊", go_reports)
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

    topbar = ctk.CTkFrame(main, fg_color="#1e293b", height=60, corner_radius=0)
    topbar.pack(fill="x")
    topbar.pack_propagate(False)
    ctk.CTkLabel(
        topbar, text="Location Management",
        font=ctk.CTkFont("Arial", 18, "bold"), text_color="white"
    ).pack(side="left", padx=25, pady=15)
    ctk.CTkLabel(topbar, text=f"👤 {session.current_user}", font=ctk.CTkFont("Arial", 12), text_color="#94a3b8").pack(side="right", padx=25)

    body = ctk.CTkFrame(main, fg_color="#0f172a", corner_radius=0)
    body.pack(fill="both", expand=True, padx=20, pady=15)

    # LEFT — Form
    form_frame = ctk.CTkFrame(body, fg_color="#1e293b", corner_radius=12, width=290)
    form_frame.pack(side="left", fill="y", padx=(0, 15))
    form_frame.pack_propagate(False)

    ctk.CTkLabel(
        form_frame, text="Add New Location",
        font=ctk.CTkFont("Arial", 14, "bold"), text_color="#38bdf8"
    ).pack(anchor="w", padx=20, pady=(18, 10))

    ctk.CTkLabel(form_frame, text="Location Name", font=ctk.CTkFont("Arial", 11, "bold"), text_color="#cbd5e1").pack(anchor="w", padx=20)
    name_entry = ctk.CTkEntry(form_frame, width=240, height=36, placeholder_text="e.g. Warehouse A", corner_radius=7)
    name_entry.pack(padx=20, pady=(2, 10))

    ctk.CTkLabel(form_frame, text="Location Code", font=ctk.CTkFont("Arial", 11, "bold"), text_color="#cbd5e1").pack(anchor="w", padx=20)
    code_entry = ctk.CTkEntry(form_frame, width=240, height=36, placeholder_text="e.g. WH-A", corner_radius=7)
    code_entry.pack(padx=20, pady=(2, 10))

    def refresh_table():
        for row in tree.get_children():
            tree.delete(row)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, location_code FROM locations ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        for r in rows:
            tree.insert("", "end", values=r)

    def confirm_add_location():
        name = name_entry.get().strip()
        code = code_entry.get().strip()
        if not name or not code:
            messagebox.showwarning("Warning", "Enter both name and code.", parent=win)
            return
        loc_id = add_location(name, code)
        if loc_id:
            messagebox.showinfo("Success", f"Location '{name}' added.", parent=win)
            name_entry.delete(0, "end")
            code_entry.delete(0, "end")
            refresh_table()
        else:
            messagebox.showerror("Error", "Could not add location (code might already exist).", parent=win)

    ctk.CTkButton(
        form_frame, text="➕  Add Location", width=240, height=38,
        fg_color="#22d3ee", hover_color="#06b6d4", text_color="#0f172a",
        font=ctk.CTkFont("Arial", 12, "bold"), corner_radius=8, command=confirm_add_location
    ).pack(padx=20, pady=10)

    # RIGHT — Table of existing locations
    right_frame = ctk.CTkFrame(body, fg_color="#1e293b", corner_radius=12)
    right_frame.pack(side="right", fill="both", expand=True)

    ctk.CTkLabel(
        right_frame, text="Existing Locations",
        font=ctk.CTkFont("Arial", 14, "bold"), text_color="#38bdf8"
    ).pack(anchor="w", padx=20, pady=(18, 10))

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

    cols = ("ID", "Name", "Code")
    tree = ttk.Treeview(right_frame, columns=cols, show="headings", height=18)
    widths = [60, 200, 150]
    for col, w in zip(cols, widths):
        tree.heading(col, text=col)
        tree.column(col, width=w, anchor="center")
    tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    refresh_table()
    win.mainloop()