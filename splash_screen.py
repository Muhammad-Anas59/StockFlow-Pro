# splash_screen.py
import customtkinter as ctk
import time

def show_splash(on_complete):
    splash = ctk.CTk()
    try:
        splash.iconbitmap("icon.ico")
    except:
        pass
    splash.title("")
    splash.resizable(False, False)
    ctk.set_appearance_mode("dark")

    splash.update_idletasks()
    x = (splash.winfo_screenwidth() // 2) - 300
    y = (splash.winfo_screenheight() // 2) - 175
    splash.geometry(f"600x350+{x}+{y}")
    splash.overrideredirect(True)

    frame = ctk.CTkFrame(splash, fg_color="#0f172a", corner_radius=0)
    frame.pack(fill="both", expand=True)

    ctk.CTkLabel(frame, text="📦", font=("Arial", 60)).pack(pady=(50, 5))

    ctk.CTkLabel(
        frame,
        text="StockFlow Pro",
        font=ctk.CTkFont("Arial", 28, "bold"),
        text_color="#38bdf8"
    ).pack()

    ctk.CTkLabel(
        frame,
        text="Professional Inventory & Sales Management",
        font=ctk.CTkFont("Arial", 12),
        text_color="#94a3b8"
    ).pack(pady=(4, 25))

    progress = ctk.CTkProgressBar(frame, width=350, height=8, progress_color="#38bdf8")
    progress.pack(pady=5)
    progress.set(0)

    status = ctk.CTkLabel(frame, text="Starting...", font=ctk.CTkFont("Arial", 11), text_color="#64748b")
    status.pack(pady=6)

    steps = [
        (0.25, "Connecting to database..."),
        (0.55, "Loading modules..."),
        (0.80, "Preparing interface..."),
        (1.0,  "Ready!"),
    ]

    def animate(index=0):
        if index < len(steps):
            val, msg = steps[index]
            progress.set(val)
            status.configure(text=msg)
            splash.after(600, animate, index + 1)
        else:
            splash.after(300, finish)

    def finish():
        splash.destroy()
        on_complete()

    splash.after(200, animate)
    splash.mainloop()