# main.py
import customtkinter as ctk
from splash_screen import show_splash

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def launch_dashboard():
    from dashboard import show_dashboard
    show_dashboard(launch_dashboard)

def start_login():
    from login import show_login
    show_login(launch_dashboard)

def start_app():
    start_login()

if __name__ == "__main__":
    show_splash(start_app)