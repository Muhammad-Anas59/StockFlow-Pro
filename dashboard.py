# dashboard.py
import customtkinter as ctk
import session
from database import get_dashboard_stats

def show_dashboard(root_callback):
    win = ctk.CTk()
    win.iconbitmap("icon.ico")
    win.title("StockFlow Pro — Dashboard")
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
    ctk.CTkLabel(
        sidebar, text="─" * 22,
        text_color="#1e293b"
    ).pack(pady=(15, 10))

    def nav_button(text, icon, command):
        ctk.CTkButton(
            sidebar, text=f"  {icon}  {text}",
            fg_color="transparent", hover_color="#1e293b",
            anchor="w", font=ctk.CTkFont("Arial", 13),
            text_color="#94a3b8", height=42,
            command=command
        ).pack(fill="x", padx=10, pady=2)

    def open_inventory():
        win.destroy()
        from inventory import show_inventory
        show_inventory(root_callback)

    nav_button("Dashboard", "🏠", lambda: None)
    nav_button("Inventory", "📋", open_inventory)

    def open_sales():
        win.destroy()
        from sales import show_sales
        show_sales(root_callback)

    nav_button("Sales", "💰", open_sales)

    def open_reports():
        win.destroy()
        from reports import show_reports
        show_reports(root_callback)

    nav_button("Reports", "📊", open_reports)

    def go_settings():
        win.destroy()
        from settings import show_settings
        show_settings(root_callback)

    nav_button("Settings", "⚙️", go_settings)

    # Logout
    def do_logout():
        win.destroy()
        from login import show_login
        show_login(root_callback)

    ctk.CTkButton(
        sidebar, text="  🚪  Logout",
        fg_color="transparent", hover_color="#1e293b",
        anchor="w", font=ctk.CTkFont("Arial", 13),
        text_color="#ef4444", height=42,
        command=do_logout
    ).pack(fill="x", padx=10, pady=2, side="bottom")

    # ── MAIN CONTENT ──
    main = ctk.CTkFrame(win, fg_color="#0f172a", corner_radius=0)
    main.pack(side="right", fill="both", expand=True)

    # Top bar
    topbar = ctk.CTkFrame(main, fg_color="#1e293b", height=60, corner_radius=0)
    topbar.pack(fill="x")
    topbar.pack_propagate(False)

    ctk.CTkLabel(
        topbar, text="Dashboard Overview",
        font=ctk.CTkFont("Arial", 18, "bold"),
        text_color="white"
    ).pack(side="left", padx=25, pady=15)

    ctk.CTkLabel(
        topbar, text="👤 Admin",
        font=ctk.CTkFont("Arial", 12),
        text_color="#94a3b8"
    ).pack(side="right", padx=25)

    # Content area
    content = ctk.CTkFrame(main, fg_color="#0f172a", corner_radius=0)
    content.pack(fill="both", expand=True, padx=25, pady=20)

    ctk.CTkLabel(
        content, text=f"Welcome back, {session.current_user}! 👋",
        font=ctk.CTkFont("Arial", 20, "bold"),
        text_color="white"
    ).pack(anchor="w", pady=(0, 5))

    ctk.CTkLabel(
        content, text="Here's what's happening with your store today.",
        font=ctk.CTkFont("Arial", 12),
        text_color="#94a3b8"
    ).pack(anchor="w", pady=(0, 20))

    # ── STATS CARDS ──
    stats = get_dashboard_stats()
    cards_data = [
        ("📦", "Total Products", str(stats[0]), "#38bdf8"),
        ("🗃️", "Total Stock", str(stats[1]), "#34d399"),
        ("⚠️", "Low Stock", str(stats[2]), "#f59e0b"),
        ("💰", "Stock Value", f"Rs {stats[3]:,}", "#a78bfa"),
    ]

    cards_frame = ctk.CTkFrame(content, fg_color="transparent")
    cards_frame.pack(fill="x", pady=(0, 20))

    for icon, title, value, color in cards_data:
        card = ctk.CTkFrame(cards_frame, fg_color="#1e293b", corner_radius=12, width=185, height=110)
        card.pack(side="left", padx=(0, 15))
        card.pack_propagate(False)

        ctk.CTkLabel(card, text=icon, font=("Arial", 28)).pack(anchor="w", padx=18, pady=(14, 2))
        ctk.CTkLabel(card, text=value, font=ctk.CTkFont("Arial", 22, "bold"), text_color=color).pack(anchor="w", padx=18)
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont("Arial", 11), text_color="#64748b").pack(anchor="w", padx=18)

    # ── QUICK ACTIONS ──
    ctk.CTkLabel(
        content, text="Quick Actions",
        font=ctk.CTkFont("Arial", 15, "bold"),
        text_color="white"
    ).pack(anchor="w", pady=(10, 10))

    actions_frame = ctk.CTkFrame(content, fg_color="transparent")
    actions_frame.pack(fill="x")

    actions = [
        ("➕  Add Product", "#38bdf8", "#0ea5e9", open_inventory),
        ("📋  View Inventory", "#34d399", "#10b981", open_inventory),
        ("📊  View Reports", "#a78bfa", "#8b5cf6", open_reports),
    ]

    for text, fg, hover, cmd in actions:
        ctk.CTkButton(
            actions_frame, text=text, width=185, height=44,
            fg_color=fg, hover_color=hover,
            text_color="#0f172a", font=ctk.CTkFont("Arial", 13, "bold"),
            corner_radius=10, command=cmd
        ).pack(side="left", padx=(0, 15))

    # ── RECENT ACTIVITY ──
    ctk.CTkLabel(
        content, text="Recent Products",
        font=ctk.CTkFont("Arial", 15, "bold"),
        text_color="white"
    ).pack(anchor="w", pady=(25, 10))

    from database import get_all_products
    import tkinter.ttk as ttk

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

    cols = ("ID", "Name", "Category", "Quantity", "Price", "Supplier")
    table_frame = ctk.CTkFrame(content, fg_color="#1e293b", corner_radius=10)
    table_frame.pack(fill="both", expand=True)

    tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=6)
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=130, anchor="center")
    tree.column("ID", width=50)
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    products = get_all_products()
    for p in products[:6]:
        tree.insert("", "end", values=p)

    win.mainloop()