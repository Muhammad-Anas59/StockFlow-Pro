# inventory.py
import customtkinter as ctk
import session
from tkinter import messagebox
import tkinter.ttk as ttk
from database import (
    get_connection,
    add_product, get_all_products,
    search_products, update_product, delete_product,
    set_product_barcode, get_product_by_barcode,
    create_carton, get_carton_by_barcode,
    add_location, get_location_by_code, log_movement,
    restock_product, get_movement_history
)
from barcode_gen import generate_sku_barcode, generate_carton_barcode

def show_inventory(root_callback):
    win = ctk.CTk()
    win.iconbitmap("icon.ico")
    win.title("StockFlow Pro — Inventory")
    win.geometry("1100x800")
    win.resizable(False, False)
    ctk.set_appearance_mode("dark")

    win.geometry("1100x800")

    win.update_idletasks()
    screen_w = win.winfo_screenwidth()
    screen_h = win.winfo_screenheight()

    x = (screen_w // 2) - 550
    y = max(20, (screen_h // 2) - 400)  # never let y go negative or too close to top

    win.geometry(f"1100x800+{x}+{y}")

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

    def go_sales():
        win.destroy()
        from sales import show_sales
        show_sales(root_callback)

    def go_locations():
        win.destroy()
        from locations import show_locations
        show_locations(root_callback)

    def go_reports():
        win.destroy()
        from reports import show_reports
        show_reports(root_callback)

    def go_settings():
        win.destroy()
        from settings import show_settings
        show_settings(root_callback)

    nav_btn("Dashboard", "🏠", go_dashboard)
    nav_btn("Inventory", "📋", lambda: None)
    nav_btn("Sales", "💰", go_sales)
    nav_btn("Locations", "📍", go_locations)
    nav_btn("Reports", "📊", go_reports)


    def go_locations():
        win.destroy()
        from locations import show_locations
        show_locations(root_callback)

    def go_reports():
        win.destroy()
        from reports import show_reports
        show_reports(root_callback)

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

    # Topbar
    topbar = ctk.CTkFrame(main, fg_color="#1e293b", height=60, corner_radius=0)
    topbar.pack(fill="x")
    topbar.pack_propagate(False)
    ctk.CTkLabel(
        topbar, text="Inventory Management",
        font=ctk.CTkFont("Arial", 18, "bold"), text_color="white"
    ).pack(side="left", padx=25, pady=15)
    ctk.CTkLabel(topbar, text=f"👤 {session.current_user}", font=ctk.CTkFont("Arial", 12), text_color="#94a3b8").pack(side="right", padx=25)

    # ── FORM + TABLE AREA ──
    body = ctk.CTkFrame(main, fg_color="#0f172a", corner_radius=0)
    body.pack(fill="both", expand=True, padx=20, pady=15)

    # LEFT — Form
    form_frame = ctk.CTkFrame(body, fg_color="#1e293b", corner_radius=12, width=290)
    form_frame.pack(side="left", fill="y", padx=(0, 15))
    form_frame.pack_propagate(False)

    ctk.CTkLabel(
        form_frame, text="Product Details",
        font=ctk.CTkFont("Arial", 13, "bold"), text_color="#38bdf8"
    ).pack(anchor="w", padx=20, pady=(10, 2))

    lbl_editing = ctk.CTkLabel(
        form_frame, text="No product selected — click a row to edit",
        font=ctk.CTkFont("Arial", 9), text_color="#64748b"
    )
    lbl_editing.pack(anchor="w", padx=20, pady=(0, 2))

    fields = {}
    field_list = [
        ("Product Name", "name"),
        ("Category", "category"),
        ("Quantity", "quantity"),
        ("Price (Rs)", "price"),
        ("Supplier", "supplier"),
    ]

    for label, key in field_list:
        ctk.CTkLabel(form_frame, text=label, font=ctk.CTkFont("Arial", 10, "bold"), text_color="#cbd5e1").pack(
            anchor="w", padx=20)
        entry = ctk.CTkEntry(form_frame, width=240, height=22, placeholder_text=f"Enter {label.lower()}",
                             corner_radius=7)
        entry.pack(padx=20, pady=(1, 1))
        fields[key] = entry

    selected_id = [None]

    def clear_form():
        for e in fields.values():
            e.delete(0, "end")
        selected_id[0] = None
        lbl_editing.configure(text="No product selected — click a row to edit", text_color="#64748b")

    def refresh_table(data=None):
        for row in tree.get_children():
            tree.delete(row)
        rows = data if data is not None else get_all_products()
        for p in rows:
            tree.insert("", "end", values=p)

    def do_add():
        n = fields["name"].get().strip()
        c = fields["category"].get().strip()
        q = fields["quantity"].get().strip()
        p = fields["price"].get().strip()
        s = fields["supplier"].get().strip()
        if not n or not q or not p:
            messagebox.showwarning("Warning", "Name, Quantity and Price are required.", parent=win)
            return
        try:
            float(p); int(q)
        except ValueError:
            messagebox.showerror("Error", "Quantity must be integer, Price must be number.", parent=win)
            return
        add_product(n, c, int(q), float(p), s)

        # Get the newly added product's ID (most recent product for this user)
        new_products = get_all_products()
        new_product_id = new_products[0][0]  # most recent, since query orders by id DESC

        barcode_value, barcode_path = generate_sku_barcode(new_product_id, n.replace(" ", ""))
        set_product_barcode(new_product_id, barcode_value)

        messagebox.showinfo("Success", f"Product added! Barcode generated: {barcode_value}", parent=win)
        clear_form()
        refresh_table()

    def do_update():
        if not selected_id[0]:
            messagebox.showwarning("Warning", "Select a product from table first.", parent=win)
            return
        n = fields["name"].get().strip()
        c = fields["category"].get().strip()
        q = fields["quantity"].get().strip()
        p = fields["price"].get().strip()
        s = fields["supplier"].get().strip()
        if not n or not q or not p:
            messagebox.showwarning("Warning", "Name, Quantity and Price are required.", parent=win)
            return
        update_product(selected_id[0], n, c, int(q), float(p), s)

        # Regenerate barcode to stay in sync with corrected name/details
        barcode_value, barcode_path = generate_sku_barcode(selected_id[0], n.replace(" ", ""))
        set_product_barcode(selected_id[0], barcode_value)

        messagebox.showinfo("Success", f"Product updated! Barcode: {barcode_value}", parent=win)
        clear_form()
        refresh_table()

    def do_delete():
        if not selected_id[0]:
            messagebox.showwarning("Warning", "Select a product to delete.", parent=win)
            return
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this product?", parent=win):
            success, msg = delete_product(selected_id[0])
            if success:
                messagebox.showinfo("Deleted", "Product deleted.", parent=win)
                clear_form()
                refresh_table()
            else:
                messagebox.showerror("Cannot Delete", msg, parent=win)
            clear_form()
            refresh_table()

    def do_restock():
        products = get_all_products()
        if not products:
            messagebox.showwarning("Warning", "No products available to restock.", parent=win)
            return

        restock_win = ctk.CTkToplevel(win)
        restock_win.title("Restock Product")
        restock_win.geometry("380x260")
        restock_win.resizable(False, False)
        restock_win.grab_set()  # keeps focus on this popup

        ctk.CTkLabel(
            restock_win, text="Restock Existing Product",
            font=ctk.CTkFont("Arial", 14, "bold"), text_color="#38bdf8"
        ).pack(pady=(20, 10))

        ctk.CTkLabel(restock_win, text="Select Product", font=ctk.CTkFont("Arial", 11, "bold")).pack(anchor="w",
                                                                                                     padx=30)

        product_names = [f"{p[0]} - {p[1]} (Current Qty: {p[3]})" for p in products]
        product_map = {f"{p[0]} - {p[1]} (Current Qty: {p[3]})": p[0] for p in products}

        dropdown = ctk.CTkComboBox(restock_win, values=product_names, width=300)
        dropdown.pack(padx=30, pady=(2, 12))
        dropdown.set(product_names[0])

        ctk.CTkLabel(restock_win, text="Quantity to Add", font=ctk.CTkFont("Arial", 11, "bold")).pack(anchor="w",
                                                                                                      padx=30)
        qty_entry = ctk.CTkEntry(restock_win, width=300, placeholder_text="e.g. 20")
        qty_entry.pack(padx=30, pady=(2, 12))

        def confirm_restock():
            selected = dropdown.get()
            qty_str = qty_entry.get().strip()
            if not qty_str:
                messagebox.showwarning("Warning", "Enter a quantity.", parent=restock_win)
                return
            try:
                qty = int(qty_str)
                if qty <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Quantity must be a positive whole number.", parent=restock_win)
                return

            product_id = product_map[selected]
            restock_product(product_id, qty)
            messagebox.showinfo("Success", f"Added {qty} units to stock.", parent=restock_win)
            restock_win.destroy()
            refresh_table()

        ctk.CTkButton(
            restock_win, text="Confirm Restock", width=300, height=38,
            fg_color="#34d399", hover_color="#10b981", text_color="#0f172a",
            font=ctk.CTkFont("Arial", 12, "bold"), command=confirm_restock
        ).pack(pady=10)

    def do_create_carton():
        products = get_all_products()
        if not products:
            messagebox.showwarning("Warning", "No products available.", parent=win)
            return

        carton_win = ctk.CTkToplevel(win)
        carton_win.title("Create Carton")
        carton_win.geometry("380x260")
        carton_win.resizable(False, False)
        carton_win.grab_set()

        ctk.CTkLabel(
            carton_win, text="Create New Carton",
            font=ctk.CTkFont("Arial", 14, "bold"), text_color="#38bdf8"
        ).pack(pady=(20, 10))

        ctk.CTkLabel(carton_win, text="Select Product (SKU)", font=ctk.CTkFont("Arial", 11, "bold")).pack(anchor="w",
                                                                                                          padx=30)

        product_names = [f"{p[0]} - {p[1]}" for p in products]
        product_map = {f"{p[0]} - {p[1]}": (p[0], p[1]) for p in products}

        dropdown = ctk.CTkComboBox(carton_win, values=product_names, width=300)
        dropdown.pack(padx=30, pady=(2, 12))
        dropdown.set(product_names[0])

        ctk.CTkLabel(carton_win, text="Units Per Carton", font=ctk.CTkFont("Arial", 11, "bold")).pack(anchor="w",
                                                                                                      padx=30)
        units_entry = ctk.CTkEntry(carton_win, width=300, placeholder_text="e.g. 5")
        units_entry.pack(padx=30, pady=(2, 12))

        def confirm_carton():
            selected = dropdown.get()
            units_str = units_entry.get().strip()
            if not units_str:
                messagebox.showwarning("Warning", "Enter units per carton.", parent=carton_win)
                return
            try:
                units = int(units_str)
                if units <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Units must be a positive whole number.", parent=carton_win)
                return

            product_id, product_name = product_map[selected]

            # First create the carton row to get its ID
            carton_id = create_carton(product_id, "TEMP", units)
            # Now generate the real barcode using that carton_id
            barcode_value, barcode_path = generate_carton_barcode(carton_id, product_name.replace(" ", ""))
            # Update the carton with the real barcode value
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE cartons SET carton_barcode=%s WHERE id=%s", (barcode_value, carton_id))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"Carton created!\nBarcode: {barcode_value}\nUnits: {units}",
                                parent=carton_win)
            carton_win.destroy()

        ctk.CTkButton(
            carton_win, text="Create Carton", width=300, height=38,
            fg_color="#a78bfa", hover_color="#8b5cf6", text_color="#0f172a",
            font=ctk.CTkFont("Arial", 12, "bold"), command=confirm_carton
        ).pack(pady=10)

    def do_scan_product():
        scan_win = ctk.CTkToplevel(win)
        scan_win.title("Scan Product")
        scan_win.geometry("420x320")
        scan_win.resizable(False, False)
        scan_win.grab_set()

        ctk.CTkLabel(
            scan_win, text="Scan / Enter Product Barcode",
            font=ctk.CTkFont("Arial", 14, "bold"), text_color="#38bdf8"
        ).pack(pady=(20, 10))

        barcode_entry = ctk.CTkEntry(scan_win, width=340, height=38, placeholder_text="Scan or type barcode...")
        barcode_entry.pack(padx=30, pady=(0, 10))
        barcode_entry.focus()

        info_label = ctk.CTkLabel(scan_win, text="", font=ctk.CTkFont("Arial", 12), text_color="#94a3b8",
                                  justify="left")
        info_label.pack(padx=30, pady=(0, 15))

        def do_lookup():
            barcode_val = barcode_entry.get().strip()
            if not barcode_val:
                return
            product = get_product_by_barcode(barcode_val)
            if not product:
                info_label.configure(text="❌ No product found with this barcode.", text_color="#ef4444")
                return

            # Adjust indices below to match your get_product_by_barcode return order
            product_id, name, category, quantity, price, supplier, created_at, barcode = product
            info_label.configure(
                text=(
                    f"✅ Found: {name}\n"
                    f"Category: {category}\n"
                    f"Quantity: {quantity}\n"
                    f"Price: Rs {price}\n"
                    f"Supplier: {supplier}"
                ),
                text_color="#34d399"
            )

        ctk.CTkButton(
            scan_win, text="🔍 Lookup", width=340, height=32,
            fg_color="#38bdf8", hover_color="#0ea5e9", text_color="#0f172a",
            font=ctk.CTkFont("Arial", 11, "bold"), command=do_lookup
        ).pack(padx=30, pady=(0, 10))

        barcode_entry.bind("<Return>", lambda e: do_lookup())

    def do_scan_carton():
        scan_win = ctk.CTkToplevel(win)
        scan_win.title("Scan Carton")
        scan_win.geometry("420x480")
        scan_win.resizable(False, False)
        scan_win.grab_set()

        ctk.CTkLabel(
            scan_win, text="Scan / Enter Carton Barcode",
            font=ctk.CTkFont("Arial", 14, "bold"), text_color="#38bdf8"
        ).pack(pady=(20, 10))

        barcode_entry = ctk.CTkEntry(scan_win, width=340, height=38, placeholder_text="Scan or type barcode...")
        barcode_entry.pack(padx=30, pady=(0, 10))
        barcode_entry.focus()  # ready for scanner input immediately

        info_label = ctk.CTkLabel(scan_win, text="", font=ctk.CTkFont("Arial", 11), text_color="#94a3b8",
                                  justify="left")
        info_label.pack(padx=30, pady=(0, 10))

        action_var = ctk.StringVar(value="received")
        location_dropdown = ctk.CTkComboBox(scan_win, values=["-- No locations yet --"], width=340)

        found_carton = [None]  # holds (carton_id, product_id, product_name, units, status)

        def do_lookup():
            barcode_val = barcode_entry.get().strip()
            if not barcode_val:
                return
            carton = get_carton_by_barcode(barcode_val)
            if not carton:
                info_label.configure(text="❌ No carton found with this barcode.", text_color="#ef4444")
                found_carton[0] = None
                return

            carton_id, product_id, product_name, carton_barcode, units, status = carton
            found_carton[0] = carton
            info_label.configure(
                text=f"✅ Found: {product_name}\nUnits per carton: {units}\nCurrent status: {status}",
                text_color="#34d399"
            )

            # Populate locations dropdown
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, location_code FROM locations")
            locs = cursor.fetchall()
            conn.close()
            if locs:
                loc_values = [f"{l[0]} - {l[1]} ({l[2]})" for l in locs]
                location_dropdown.configure(values=loc_values)
                location_dropdown.set(loc_values[0])
            else:
                location_dropdown.configure(values=["-- No locations yet, add one first --"])
                location_dropdown.set("-- No locations yet, add one first --")

        ctk.CTkButton(
            scan_win, text="🔍 Lookup", width=340, height=32,
            fg_color="#38bdf8", hover_color="#0ea5e9", text_color="#0f172a",
            font=ctk.CTkFont("Arial", 11, "bold"), command=do_lookup
        ).pack(padx=30, pady=(0, 15))

        barcode_entry.bind("<Return>", lambda e: do_lookup())  # scanner "enters" automatically

        def show_history():
            if not found_carton[0]:
                messagebox.showwarning("Warning", "Look up a valid carton first.", parent=scan_win)
                return

            carton_id = found_carton[0][0]
            history = get_movement_history(carton_id)

            hist_win = ctk.CTkToplevel(scan_win)
            hist_win.title("Movement History")
            hist_win.geometry("400x350")
            hist_win.grab_set()

            ctk.CTkLabel(
                hist_win, text="Scan History", font=ctk.CTkFont("Arial", 14, "bold"), text_color="#38bdf8"
            ).pack(pady=(15, 10))

            if not history:
                ctk.CTkLabel(hist_win, text="No movement history yet.", text_color="#94a3b8").pack(pady=20)
            else:
                for entry_id, loc_name, action, scanned_at in history:
                    loc_display = loc_name if loc_name else "N/A"
                    ctk.CTkLabel(
                        hist_win,
                        text=f"{scanned_at}  —  {action.upper()}  —  {loc_display}",
                        font=ctk.CTkFont("Arial", 11), text_color="white", anchor="w"
                    ).pack(anchor="w", padx=20, pady=3)

        ctk.CTkButton(
            scan_win, text="📜 View History", width=340, height=30,
            fg_color="#64748b", hover_color="#475569", text_color="white",
            font=ctk.CTkFont("Arial", 10, "bold"), command=show_history
        ).pack(padx=30, pady=(0, 10))

        ctk.CTkLabel(scan_win, text="Action", font=ctk.CTkFont("Arial", 11, "bold")).pack(anchor="w", padx=30)
        action_menu = ctk.CTkComboBox(scan_win, values=["received", "moved", "opened"], variable=action_var, width=340)
        action_menu.pack(padx=30, pady=(2, 10))

        ctk.CTkLabel(scan_win, text="Location", font=ctk.CTkFont("Arial", 11, "bold")).pack(anchor="w", padx=30)
        location_dropdown.pack(padx=30, pady=(2, 15))

        def confirm_scan():
            if not found_carton[0]:
                messagebox.showwarning("Warning", "Look up a valid carton barcode first.", parent=scan_win)
                return

            carton_id = found_carton[0][0]
            action = action_var.get()
            loc_selection = location_dropdown.get()

            location_id = None
            if " - " in loc_selection and "No locations" not in loc_selection:
                location_id = int(loc_selection.split(" - ")[0])
            elif action != "opened":
                messagebox.showwarning("Warning", "Select a valid location (or add one first).", parent=scan_win)
                return

            log_movement(carton_id, location_id, action)
            messagebox.showinfo("Success", f"Logged: {action} for carton.", parent=scan_win)
            scan_win.destroy()

        ctk.CTkButton(
            scan_win, text="✅ Confirm Scan", width=340, height=38,
            fg_color="#34d399", hover_color="#10b981", text_color="#0f172a",
            font=ctk.CTkFont("Arial", 12, "bold"), command=confirm_scan
        ).pack(pady=5)


    def do_manage_locations():
        loc_win = ctk.CTkToplevel(win)
        loc_win.title("Manage Locations")
        loc_win.geometry("400x320")
        loc_win.resizable(False, False)
        loc_win.grab_set()

        ctk.CTkLabel(
            loc_win, text="Add / Assign Location",
            font=ctk.CTkFont("Arial", 14, "bold"), text_color="#38bdf8"
        ).pack(pady=(20, 10))

        ctk.CTkLabel(loc_win, text="Location Name", font=ctk.CTkFont("Arial", 11, "bold")).pack(anchor="w", padx=30)
        name_entry = ctk.CTkEntry(loc_win, width=320, placeholder_text="e.g. Warehouse A")
        name_entry.pack(padx=30, pady=(2, 10))

        ctk.CTkLabel(loc_win, text="Location Code", font=ctk.CTkFont("Arial", 11, "bold")).pack(anchor="w", padx=30)
        code_entry = ctk.CTkEntry(loc_win, width=320, placeholder_text="e.g. WH-A")
        code_entry.pack(padx=30, pady=(2, 10))

        def confirm_location():
            name = name_entry.get().strip()
            code = code_entry.get().strip()
            if not name or not code:
                messagebox.showwarning("Warning", "Enter both name and code.", parent=loc_win)
                return
            loc_id = add_location(name, code)
            if loc_id:
                messagebox.showinfo("Success", f"Location '{name}' added with code '{code}'.", parent=loc_win)
                loc_win.destroy()
            else:
                messagebox.showerror("Error", "Could not add location (code might already exist).", parent=loc_win)

        ctk.CTkButton(
            loc_win, text="Add Location", width=320, height=38,
            fg_color="#22d3ee", hover_color="#06b6d4", text_color="#0f172a",
            font=ctk.CTkFont("Arial", 12, "bold"), command=confirm_location
        ).pack(pady=10)

        ctk.CTkLabel(
            loc_win, text="Tip: create locations first, then use\n'Scan Carton' to assign cartons to them.",
            font=ctk.CTkFont("Arial", 9), text_color="#64748b"
        ).pack(pady=(10, 0))

    btn_configs = [
        ("➕  Add Product", "#38bdf8", "#0ea5e9", do_add),
        ("✏️  Update", "#34d399", "#10b981", do_update),
        ("📦  Restock", "#fbbf24", "#f59e0b", do_restock),
        ("📮  Create Carton", "#a78bfa", "#8b5cf6", do_create_carton),
        ("🔍  Scan Carton", "#38bdf8", "#0ea5e9", do_scan_carton),
        ("🏷️  Scan Product", "#06b6d4", "#0891b2", do_scan_product),
        ("🗑️  Delete", "#ef4444", "#dc2626", do_delete),
        ("🔄  Clear", "#475569", "#334155", clear_form),
    ]

    for text, fg, hover, cmd in btn_configs:
        ctk.CTkButton(
            form_frame, text=text, width=240, height=24,
            fg_color=fg, hover_color=hover,
            text_color="#0f172a" if fg != "#475569" else "white",
            font=ctk.CTkFont("Arial", 9, "bold"),
            corner_radius=6, command=cmd
        ).pack(padx=20, pady=1)

    # RIGHT — Table
    right_frame = ctk.CTkFrame(body, fg_color="#1e293b", corner_radius=12)
    right_frame.pack(side="right", fill="both", expand=True)

    # Search bar
    search_bar = ctk.CTkFrame(right_frame, fg_color="transparent")
    search_bar.pack(fill="x", padx=20, pady=(15, 10))

    ctk.CTkLabel(search_bar, text="🔍", font=("Arial", 16)).pack(side="left")
    txt_search = ctk.CTkEntry(search_bar, width=280, height=36, placeholder_text="Search products...", corner_radius=7)
    txt_search.pack(side="left", padx=8)

    def do_search():
        kw = txt_search.get().strip()
        if kw:
            refresh_table(search_products(kw))
        else:
            refresh_table()

    ctk.CTkButton(
        search_bar, text="Search", width=90, height=36,
        fg_color="#38bdf8", hover_color="#0ea5e9",
        text_color="#0f172a", font=ctk.CTkFont("Arial", 12, "bold"),
        corner_radius=7, command=do_search
    ).pack(side="left")

    ctk.CTkButton(
        search_bar, text="Show All", width=90, height=36,
        fg_color="#38bdf8", hover_color="#0ea5e9",
        text_color="white", font=ctk.CTkFont("Arial", 12, "bold"),
        corner_radius=7, command=lambda: refresh_table()
    ).pack(side="left", padx=8)

    # Treeview table
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

    cols = ("ID", "Name", "Category", "Qty", "Price", "Supplier", "Date")
    tree = ttk.Treeview(right_frame, columns=cols, show="headings", height=15)
    widths = [45, 160, 110, 60, 90, 130, 110]
    for col, w in zip(cols, widths):
        tree.heading(col, text=col)
        tree.column(col, width=w, anchor="center")
    tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def on_row_select(event):
        selected = tree.selection()
        if not selected:
            return
        row = tree.item(selected[0])["values"]
        if not row:
            return
        clear_form()
        selected_id[0] = row[0]
        fields["name"].insert(0, str(row[1]))
        fields["category"].insert(0, str(row[2]))
        fields["quantity"].insert(0, str(row[3]))
        fields["price"].insert(0, str(row[4]))
        fields["supplier"].insert(0, str(row[5]))
        lbl_editing.configure(text=f"✏️ Editing: {row[1]} (ID: {row[0]})", text_color="#34d399")

    tree.bind("<<TreeviewSelect>>", on_row_select)
    refresh_table()
    win.mainloop()