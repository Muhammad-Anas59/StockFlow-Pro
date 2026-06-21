# settings.py
import customtkinter as ctk
from tkinter import messagebox
import session
from database import get_user_info, verify_login, update_password

def show_settings(root_callback):
    win = ctk.CTk()
    win.iconbitmap("icon.ico")
    win.title("StockFlow Pro — Settings")
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
        font=ctk.CTkFont("Arial", 16, "bold"), text_color="#38bdf8"
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

    nav_btn("Dashboard", "🏠", go_dashboard)
    nav_btn("Inventory", "📋", go_inventory)
    nav_btn("Sales", "💰", go_sales)
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

    topbar = ctk.CTkFrame(main, fg_color="#1e293b", height=60, corner_radius=0)
    topbar.pack(fill="x")
    topbar.pack_propagate(False)
    ctk.CTkLabel(
        topbar, text="Settings",
        font=ctk.CTkFont("Arial", 18, "bold"), text_color="white"
    ).pack(side="left", padx=25, pady=15)
    ctk.CTkLabel(
        topbar, text=f"👤 {session.current_user}",
        font=ctk.CTkFont("Arial", 12), text_color="#94a3b8"
    ).pack(side="right", padx=25)

    content = ctk.CTkFrame(main, fg_color="#0f172a", corner_radius=0)
    content.pack(fill="both", expand=True, padx=20, pady=15)

    body = ctk.CTkFrame(content, fg_color="transparent")
    body.pack(fill="both", expand=True)

    # ── LEFT — Account Info ──
    info_card = ctk.CTkFrame(body, fg_color="#1e293b", corner_radius=12, width=350)
    info_card.pack(side="left", fill="y", padx=(0, 15))
    info_card.pack_propagate(False)

    ctk.CTkLabel(
        info_card, text="Account Information",
        font=ctk.CTkFont("Arial", 15, "bold"), text_color="#38bdf8"
    ).pack(anchor="w", padx=20, pady=(20, 15))

    user_info = get_user_info(session.current_user)
    if user_info:
        uname, email, created_at = user_info
    else:
        uname, email, created_at = session.current_user, "—", "—"

    def info_row(label, value):
        ctk.CTkLabel(info_card, text=label, font=ctk.CTkFont("Arial", 11, "bold"), text_color="#64748b").pack(anchor="w", padx=20, pady=(8, 0))
        ctk.CTkLabel(info_card, text=str(value), font=ctk.CTkFont("Arial", 13), text_color="white").pack(anchor="w", padx=20)

    info_row("Username", uname)
    info_row("Email", email if email else "Not provided")
    info_row("Member Since", str(created_at)[:10] if created_at != "—" else "—")

    # ── About section (inside same card, below info) ──
    ctk.CTkLabel(info_card, text="─" * 30, text_color="#334155").pack(pady=(20, 10))
    ctk.CTkLabel(
        info_card, text="About StockFlow Pro",
        font=ctk.CTkFont("Arial", 13, "bold"), text_color="#38bdf8"
    ).pack(anchor="w", padx=20, pady=(0, 8))
    ctk.CTkLabel(
        info_card, text="Version 1.0\nBuilt with Python, CustomTkinter & MySQL\nInventory & Sales Management System",
        font=ctk.CTkFont("Arial", 11), text_color="#94a3b8", justify="left"
    ).pack(anchor="w", padx=20)

    # ── RIGHT — Change Password ──
    pass_card = ctk.CTkFrame(body, fg_color="#1e293b", corner_radius=12)
    pass_card.pack(side="right", fill="both", expand=True)

    ctk.CTkLabel(
        pass_card, text="Change Password",
        font=ctk.CTkFont("Arial", 15, "bold"), text_color="#38bdf8"
    ).pack(anchor="w", padx=30, pady=(20, 15))

    ctk.CTkLabel(pass_card, text="Current Password", font=ctk.CTkFont("Arial", 12, "bold"), text_color="#cbd5e1").pack(anchor="w", padx=30)
    txt_current = ctk.CTkEntry(pass_card, width=320, height=40, placeholder_text="Enter current password", show="•", corner_radius=8)
    txt_current.pack(padx=30, pady=(4, 14))

    ctk.CTkLabel(pass_card, text="New Password", font=ctk.CTkFont("Arial", 12, "bold"), text_color="#cbd5e1").pack(anchor="w", padx=30)
    txt_new = ctk.CTkEntry(pass_card, width=320, height=40, placeholder_text="Enter new password", show="•", corner_radius=8)
    txt_new.pack(padx=30, pady=(4, 14))

    ctk.CTkLabel(pass_card, text="Confirm New Password", font=ctk.CTkFont("Arial", 12, "bold"), text_color="#cbd5e1").pack(anchor="w", padx=30)
    txt_confirm = ctk.CTkEntry(pass_card, width=320, height=40, placeholder_text="Confirm new password", show="•", corner_radius=8)
    txt_confirm.pack(padx=30, pady=(4, 20))

    def do_change_password():
        current = txt_current.get().strip()
        new = txt_new.get().strip()
        confirm = txt_confirm.get().strip()

        if not current or not new or not confirm:
            messagebox.showwarning("Warning", "Please fill all fields.", parent=win)
            return
        if not verify_login(session.current_user, current):
            messagebox.showerror("Error", "Current password is incorrect.", parent=win)
            return
        if new != confirm:
            messagebox.showerror("Error", "New passwords do not match.", parent=win)
            return
        if len(new) < 6:
            messagebox.showwarning("Warning", "Password must be at least 6 characters.", parent=win)
            return

        update_password(session.current_user, new)
        messagebox.showinfo("Success", "Password changed successfully!", parent=win)
        txt_current.delete(0, "end")
        txt_new.delete(0, "end")
        txt_confirm.delete(0, "end")

    ctk.CTkButton(
        pass_card, text="Update Password", width=320, height=42,
        fg_color="#38bdf8", hover_color="#0ea5e9", text_color="#0f172a",
        font=ctk.CTkFont("Arial", 13, "bold"), corner_radius=8,
        command=do_change_password
    ).pack(padx=30)

    win.mainloop()