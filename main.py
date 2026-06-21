# main.py
import customtkinter as ctk
from splash_screen import show_splash
import sys
import os

def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

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