# forgot_password.py
import customtkinter as ctk
from tkinter import messagebox
from database import user_exists, update_password

def show_forgot(on_back):
    win = ctk.CTk()
    win.title("StockFlow Pro — Reset Password")
    win.geometry("500x500")
    win.resizable(False, False)
    ctk.set_appearance_mode("dark")

    win.update_idletasks()
    x = (win.winfo_screenwidth() // 2) - 250
    y = (win.winfo_screenheight() // 2) - 250
    win.geometry(f"500x500+{x}+{y}")

    frame = ctk.CTkFrame(win, fg_color="#1e293b", corner_radius=0)
    frame.pack(fill="both", expand=True)

    ctk.CTkLabel(frame, text="🔑", font=("Arial", 45)).pack(pady=(45, 5))
    ctk.CTkLabel(
        frame, text="Reset Password",
        font=ctk.CTkFont("Arial", 22, "bold"),
        text_color="#38bdf8"
    ).pack()
    ctk.CTkLabel(
        frame, text="Enter your details to reset password",
        font=ctk.CTkFont("Arial", 11),
        text_color="#94a3b8"
    ).pack(pady=(4, 25))

    # Username
    ctk.CTkLabel(frame, text="Username", font=ctk.CTkFont("Arial", 12, "bold"), text_color="#cbd5e1").pack(anchor="w", padx=70)
    txt_user = ctk.CTkEntry(frame, width=310, height=42, placeholder_text="Enter your username", corner_radius=8)
    txt_user.pack(padx=70, pady=(4, 14))

    # New Password
    ctk.CTkLabel(frame, text="New Password", font=ctk.CTkFont("Arial", 12, "bold"), text_color="#cbd5e1").pack(anchor="w", padx=70)
    txt_new = ctk.CTkEntry(frame, width=310, height=42, placeholder_text="Enter new password", show="•", corner_radius=8)
    txt_new.pack(padx=70, pady=(4, 14))

    # Confirm Password
    ctk.CTkLabel(frame, text="Confirm Password", font=ctk.CTkFont("Arial", 12, "bold"), text_color="#cbd5e1").pack(anchor="w", padx=70)
    txt_confirm = ctk.CTkEntry(frame, width=310, height=42, placeholder_text="Confirm new password", show="•", corner_radius=8)
    txt_confirm.pack(padx=70, pady=(4, 22))

    def do_reset():
        u = txt_user.get().strip()
        np = txt_new.get().strip()
        cp = txt_confirm.get().strip()
        if not u or not np or not cp:
            messagebox.showwarning("Warning", "Please fill all fields.", parent=win)
            return
        if np != cp:
            messagebox.showerror("Error", "Passwords do not match.", parent=win)
            return
        if len(np) < 6:
            messagebox.showwarning("Warning", "Password must be at least 6 characters.", parent=win)
            return
        if not user_exists(u):
            messagebox.showerror("Error", "Username not found.", parent=win)
            return
        update_password(u, np)
        messagebox.showinfo("Success", "Password reset! Please login.", parent=win)
        win.destroy()
        from login import show_login
        show_login(on_back)

    ctk.CTkButton(
        frame, text="Reset Password", width=310, height=44,
        fg_color="#38bdf8", hover_color="#0ea5e9",
        text_color="#0f172a", font=ctk.CTkFont("Arial", 14, "bold"),
        corner_radius=8, command=do_reset
    ).pack(padx=70)

    def go_back():
        win.destroy()
        from login import show_login
        show_login(on_back)

    ctk.CTkButton(
        frame, text="← Back to Login", fg_color="transparent",
        text_color="#38bdf8", hover=False,
        font=ctk.CTkFont("Arial", 12), command=go_back
    ).pack(pady=(12, 0))

    win.mainloop()