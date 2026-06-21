# sign_up.py
import customtkinter as ctk
from tkinter import messagebox
from database import user_exists, register_user

def show_signup(on_success):
    win = ctk.CTk()
    win.title("StockFlow Pro — Sign Up")
    win.geometry("500x560")
    win.resizable(False, False)
    ctk.set_appearance_mode("dark")

    win.update_idletasks()
    x = (win.winfo_screenwidth() // 2) - 250
    y = (win.winfo_screenheight() // 2) - 280
    win.geometry(f"500x560+{x}+{y}")

    frame = ctk.CTkFrame(win, fg_color="#1e293b", corner_radius=0)
    frame.pack(fill="both", expand=True)

    ctk.CTkLabel(frame, text="📝", font=("Arial", 45)).pack(pady=(35, 5))
    ctk.CTkLabel(
        frame, text="Create Account",
        font=ctk.CTkFont("Arial", 22, "bold"),
        text_color="#38bdf8"
    ).pack()
    ctk.CTkLabel(
        frame, text="Sign up to start using StockFlow Pro",
        font=ctk.CTkFont("Arial", 11),
        text_color="#94a3b8"
    ).pack(pady=(4, 20))

    # Username
    ctk.CTkLabel(frame, text="Username", font=ctk.CTkFont("Arial", 12, "bold"), text_color="#cbd5e1").pack(anchor="w", padx=70)
    txt_user = ctk.CTkEntry(frame, width=310, height=40, placeholder_text="Choose a username", corner_radius=8)
    txt_user.pack(padx=70, pady=(4, 10))

    # Email
    ctk.CTkLabel(frame, text="Email", font=ctk.CTkFont("Arial", 12, "bold"), text_color="#cbd5e1").pack(anchor="w", padx=70)
    txt_email = ctk.CTkEntry(frame, width=310, height=40, placeholder_text="Enter your email", corner_radius=8)
    txt_email.pack(padx=70, pady=(4, 10))

    # Password
    ctk.CTkLabel(frame, text="Password", font=ctk.CTkFont("Arial", 12, "bold"), text_color="#cbd5e1").pack(anchor="w", padx=70)
    txt_pass = ctk.CTkEntry(frame, width=310, height=40, placeholder_text="Create a password", show="•", corner_radius=8)
    txt_pass.pack(padx=70, pady=(4, 10))

    # Confirm Password
    ctk.CTkLabel(frame, text="Confirm Password", font=ctk.CTkFont("Arial", 12, "bold"), text_color="#cbd5e1").pack(anchor="w", padx=70)
    txt_confirm = ctk.CTkEntry(frame, width=310, height=40, placeholder_text="Confirm password", show="•", corner_radius=8)
    txt_confirm.pack(padx=70, pady=(4, 18))

    def do_signup():
        u = txt_user.get().strip()
        e = txt_email.get().strip()
        p = txt_pass.get().strip()
        cp = txt_confirm.get().strip()

        if not u or not p or not cp:
            messagebox.showwarning("Warning", "Username and password are required.", parent=win)
            return
        if p != cp:
            messagebox.showerror("Error", "Passwords do not match.", parent=win)
            return
        if len(p) < 6:
            messagebox.showwarning("Warning", "Password must be at least 6 characters.", parent=win)
            return
        if user_exists(u):
            messagebox.showerror("Error", "Username already taken. Choose another.", parent=win)
            return

        register_user(u, p, e)
        messagebox.showinfo("Success", "Account created! Please login.", parent=win)
        win.destroy()
        from login import show_login
        show_login(on_success)

    ctk.CTkButton(
        frame, text="Create Account", width=310, height=44,
        fg_color="#38bdf8", hover_color="#0ea5e9", text_color="#0f172a",
        font=ctk.CTkFont("Arial", 14, "bold"), corner_radius=8,
        command=do_signup
    ).pack(padx=70)

    def go_back():
        win.destroy()
        from login import show_login
        show_login(on_success)

    ctk.CTkButton(
        frame, text="← Back to Login", fg_color="transparent",
        text_color="#38bdf8", hover=False, font=ctk.CTkFont("Arial", 12),
        command=go_back
    ).pack(pady=(14, 0))

    win.mainloop()