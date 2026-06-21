# login.py
import customtkinter as ctk
from tkinter import messagebox
from database import verify_login

def show_login(on_success):
    win = ctk.CTk()
    win.title("StockFlow Pro — Login")
    win.geometry("900x540")
    win.resizable(False, False)
    ctk.set_appearance_mode("dark")

    win.update_idletasks()
    x = (win.winfo_screenwidth() // 2) - 450
    y = (win.winfo_screenheight() // 2) - 270
    win.geometry(f"900x540+{x}+{y}")

    # ── LEFT PANEL ──
    left = ctk.CTkFrame(win, width=400, fg_color="#0f172a", corner_radius=0)
    left.pack(side="left", fill="y")
    left.pack_propagate(False)

    ctk.CTkLabel(left, text="📦", font=("Arial", 58)).pack(pady=(90, 5))
    ctk.CTkLabel(
        left,
        text="StockFlow Pro",
        font=ctk.CTkFont("Arial", 24, "bold"),
        text_color="#38bdf8"
    ).pack()
    ctk.CTkLabel(
        left,
        text="Inventory & Sales Management",
        font=ctk.CTkFont("Arial", 12),
        text_color="#94a3b8"
    ).pack(pady=(6, 0))
    ctk.CTkLabel(
        left,
        text="Track stock • Manage sales\nGrow your business",
        font=ctk.CTkFont("Arial", 11),
        text_color="#475569",
        justify="center"
    ).pack(pady=(12, 0))

    # ── RIGHT PANEL ──
    right = ctk.CTkFrame(win, fg_color="#1e293b", corner_radius=0)
    right.pack(side="right", fill="both", expand=True)

    ctk.CTkLabel(
        right,
        text="Welcome Back 👋",
        font=ctk.CTkFont("Arial", 22, "bold"),
        text_color="white"
    ).pack(pady=(80, 4))

    ctk.CTkLabel(
        right,
        text="Sign in to your account",
        font=ctk.CTkFont("Arial", 12),
        text_color="#94a3b8"
    ).pack(pady=(0, 30))

    # Username
    ctk.CTkLabel(right, text="Username", font=ctk.CTkFont("Arial", 12, "bold"), text_color="#cbd5e1").pack(anchor="w", padx=70)
    txt_user = ctk.CTkEntry(right, width=310, height=42, placeholder_text="Enter username", corner_radius=8)
    txt_user.pack(padx=70, pady=(4, 14))

    # Password
    ctk.CTkLabel(right, text="Password", font=ctk.CTkFont("Arial", 12, "bold"), text_color="#cbd5e1").pack(anchor="w", padx=70)
    txt_pass = ctk.CTkEntry(right, width=310, height=42, placeholder_text="Enter password", show="•", corner_radius=8)
    txt_pass.pack(padx=70, pady=(4, 6))

    # Forgot link
    def open_forgot():
        win.destroy()
        from forgot_password import show_forgot
        show_forgot(on_success)

    ctk.CTkButton(
        right, text="Forgot Password?", fg_color="transparent",
        text_color="#38bdf8", hover=False,
        font=ctk.CTkFont("Arial", 11), command=open_forgot, width=80
    ).pack(anchor="e", padx=70)

    # Login button
    def do_login():
        u = txt_user.get().strip()
        p = txt_pass.get().strip()
        if not u or not p:
            messagebox.showwarning("Warning", "Please fill in all fields.", parent=win)
            return
        if verify_login(u, p):
            import session
            session.current_user = u
            win.destroy()
            on_success()
        else:
            messagebox.showerror("Error", "Invalid username or password.", parent=win)
            txt_pass.delete(0, "end")

    ctk.CTkButton(
        right, text="Sign In", width=310, height=44,
        fg_color="#10b981", hover_color="#059669",
        text_color="#0f172a", font=ctk.CTkFont("Arial", 14, "bold"),
        corner_radius=8, command=do_login
    ).pack(padx=70, pady=18)

    def open_signup():
        win.destroy()
        from sign_up import show_signup
        show_signup(on_success)

    signup_row = ctk.CTkFrame(right, fg_color="transparent")
    signup_row.pack()
    ctk.CTkLabel(signup_row, text="Don't have an account?", font=ctk.CTkFont("Arial", 11), text_color="#94a3b8").pack(
        side="left")
    ctk.CTkButton(
        signup_row, text="Sign Up", fg_color="transparent",
        text_color="#38bdf8", hover=False, font=ctk.CTkFont("Arial", 11, "bold"),
        width=50, command=open_signup
    ).pack(side="left")

    win.bind("<Return>", lambda e: do_login())
    win.mainloop()