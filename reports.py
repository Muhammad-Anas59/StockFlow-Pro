# reports.py
import customtkinter as ctk
import session
from tkinter import messagebox, filedialog
import tkinter.ttk as ttk
from datetime import datetime
from database import get_sales_stats, get_top_products, get_revenue_last_7_days, get_full_sales_summary

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def show_reports(root_callback):
    win = ctk.CTk()
    win.iconbitmap("icon.ico")
    win.title("StockFlow Pro — Reports")
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

    nav_btn("Dashboard", "🏠", go_dashboard)
    nav_btn("Inventory", "📋", go_inventory)
    nav_btn("Sales", "💰", go_sales)
    nav_btn("Reports", "📊", lambda: None)

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

    topbar = ctk.CTkFrame(main, fg_color="#1e293b", height=60, corner_radius=0)
    topbar.pack(fill="x")
    topbar.pack_propagate(False)
    ctk.CTkLabel(
        topbar, text="Reports & Analytics",
        font=ctk.CTkFont("Arial", 18, "bold"), text_color="white"
    ).pack(side="left", padx=25, pady=15)
    ctk.CTkLabel(topbar, text=f"👤 {session.current_user}", font=ctk.CTkFont("Arial", 12), text_color="#94a3b8").pack(side="right", padx=25)

    content = ctk.CTkFrame(main, fg_color="#0f172a", corner_radius=0)
    content.pack(fill="both", expand=True, padx=20, pady=15)

    # ── CHARTS ROW ──
    charts_row = ctk.CTkFrame(content, fg_color="transparent")
    charts_row.pack(fill="x", pady=(0, 15))

    # Chart styling helper
    plt.rcParams["text.color"] = "#cbd5e1"
    plt.rcParams["axes.labelcolor"] = "#cbd5e1"
    plt.rcParams["xtick.color"] = "#94a3b8"
    plt.rcParams["ytick.color"] = "#94a3b8"

    # Chart 1 — Top Products
    chart1_frame = ctk.CTkFrame(charts_row, fg_color="#1e293b", corner_radius=12, width=520, height=280)
    chart1_frame.pack(side="left", padx=(0, 15))
    chart1_frame.pack_propagate(False)
    ctk.CTkLabel(chart1_frame, text="Top Products by Revenue", font=ctk.CTkFont("Arial", 13, "bold"), text_color="#38bdf8").pack(anchor="w", padx=15, pady=(12, 0))

    top_products = get_top_products(5)
    fig1 = plt.Figure(figsize=(5, 2.6), facecolor="#1e293b")
    ax1 = fig1.add_subplot(111)
    ax1.set_facecolor("#1e293b")
    if top_products:
        names = [p[0] for p in top_products]
        revenue = [float(p[2]) for p in top_products]
        bars = ax1.bar(names, revenue, color="#38bdf8")
        ax1.bar_label(bars, fmt="Rs%.0f", color="#cbd5e1", fontsize=8)
    else:
        ax1.text(0.5, 0.5, "No sales yet", ha="center", va="center", color="#64748b")
    for spine in ax1.spines.values():
        spine.set_color("#334155")
    fig1.tight_layout()
    canvas1 = FigureCanvasTkAgg(fig1, master=chart1_frame)
    canvas1.get_tk_widget().pack(padx=10, pady=5, fill="both", expand=True)
    canvas1.draw()

    # Chart 2 — Revenue Trend (last 7 days)
    chart2_frame = ctk.CTkFrame(charts_row, fg_color="#1e293b", corner_radius=12, width=520, height=280)
    chart2_frame.pack(side="left")
    chart2_frame.pack_propagate(False)
    ctk.CTkLabel(chart2_frame, text="Revenue — Last 7 Days", font=ctk.CTkFont("Arial", 13, "bold"), text_color="#38bdf8").pack(anchor="w", padx=15, pady=(12, 0))

    revenue_trend = get_revenue_last_7_days()
    fig2 = plt.Figure(figsize=(5, 2.6), facecolor="#1e293b")
    ax2 = fig2.add_subplot(111)
    ax2.set_facecolor("#1e293b")
    if revenue_trend:
        days = [str(r[0]) for r in revenue_trend]
        revs = [float(r[1]) for r in revenue_trend]
        ax2.plot(days, revs, color="#34d399", marker="o", linewidth=2)
        ax2.fill_between(days, revs, color="#34d399", alpha=0.15)
        ax2.tick_params(axis="x", rotation=20, labelsize=8)
    else:
        ax2.text(0.5, 0.5, "No sales in last 7 days", ha="center", va="center", color="#64748b")
    for spine in ax2.spines.values():
        spine.set_color("#334155")
    fig2.tight_layout()
    canvas2 = FigureCanvasTkAgg(fig2, master=chart2_frame)
    canvas2.get_tk_widget().pack(padx=10, pady=5, fill="both", expand=True)
    canvas2.draw()

    # ── SUMMARY TABLE ──
    table_header = ctk.CTkFrame(content, fg_color="transparent")
    table_header.pack(fill="x", pady=(0, 8))

    ctk.CTkLabel(
        table_header, text="Sales Summary by Product",
        font=ctk.CTkFont("Arial", 14, "bold"), text_color="white"
    ).pack(side="left")

    summary_data = get_full_sales_summary()
    stats = get_sales_stats()

    def export_pdf():
        if not summary_data:
            messagebox.showwarning("Warning", "No sales data to export yet.", parent=win)
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"StockFlow_Report_{datetime.now().strftime('%Y%m%d')}.pdf"
        )
        if not file_path:
            return
        try:
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = [
                Paragraph("StockFlow Pro — Sales Report", styles["Title"]),
                Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y %I:%M %p')}", styles["Normal"]),
                Spacer(1, 12),
                Paragraph(
                    f"Total Sales: {stats[0]}&nbsp;&nbsp;&nbsp; "
                    f"Total Revenue: Rs {stats[1]:,.0f}&nbsp;&nbsp;&nbsp; "
                    f"Items Sold: {stats[2]}", styles["Normal"]
                ),
                Spacer(1, 20),
            ]
            table_data = [["Product", "Category", "Qty Sold", "Revenue (Rs)"]]
            for row in summary_data:
                table_data.append([row[0], row[1] or "-", str(row[2]), f"{float(row[3]):,.2f}"])

            t = Table(table_data, colWidths=[160, 130, 80, 120])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 11),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")]),
                ("FONTSIZE", (0, 1), (-1, -1), 10),
            ]))
            elements.append(t)
            doc.build(elements)
            messagebox.showinfo("Success", f"Report saved to:\n{file_path}", parent=win)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save PDF:\n{e}", parent=win)

    ctk.CTkButton(
        table_header, text="📄  Export PDF Report", width=180, height=36,
        fg_color="#38bdf8", hover_color="#0ea5e9",
        text_color="#0f172a", font=ctk.CTkFont("Arial", 12, "bold"),
        corner_radius=8, command=export_pdf
    ).pack(side="right")

    table_frame = ctk.CTkFrame(content, fg_color="#1e293b", corner_radius=12)
    table_frame.pack(fill="both", expand=True)

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

    cols = ("Product", "Category", "Qty Sold", "Revenue (Rs)")
    tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=8)
    widths = [220, 150, 100, 150]
    for col, w in zip(cols, widths):
        tree.heading(col, text=col)
        tree.column(col, width=w, anchor="center")
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    for row in summary_data:
        tree.insert("", "end", values=(row[0], row[1] or "-", row[2], f"{float(row[3]):,.2f}"))

    win.mainloop()