# database.py
import mysql.connector
import bcrypt
from config import DB_CONFIG

def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as e:
        print(f"Database Error: {e}")
        return None

def verify_login(username, password):
    conn = get_connection()
    if not conn:
        return False
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username=%s", (username,))
    result = cursor.fetchone()
    conn.close()
    if not result:
        return False
    stored_hash = result[0].encode("utf-8")
    return bcrypt.checkpw(password.encode("utf-8"), stored_hash)

def user_exists(username):
    conn = get_connection()
    if not conn:
        return None
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    result = cursor.fetchone()
    conn.close()
    return result

def update_password(username, new_password):
    conn = get_connection()
    cursor = conn.cursor()
    hashed = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    cursor.execute("UPDATE users SET password=%s WHERE username=%s", (hashed, username))
    conn.commit()
    conn.close()

def add_product(name, category, quantity, price, supplier):
    conn = get_connection()
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (name, category, quantity, price, supplier) VALUES (%s,%s,%s,%s,%s)",
        (name, category, quantity, price, supplier)
    )
    conn.commit()
    conn.close()
def restock_product(product_id, quantity_to_add):
    conn = get_connection()
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE products SET quantity = quantity + %s WHERE id=%s",
        (quantity_to_add, product_id)
    )
    conn.commit()
    conn.close()

def get_all_products():
    conn = get_connection()
    if not conn:
        return []
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def search_products(keyword):
    conn = get_connection()
    if not conn:
        return []
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM products WHERE name LIKE %s OR category LIKE %s OR supplier LIKE %s",
        (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
    )
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_product(pid, name, category, quantity, price, supplier):
    conn = get_connection()
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE products SET name=%s, category=%s, quantity=%s, price=%s, supplier=%s WHERE id=%s",
        (name, category, quantity, price, supplier, pid)
    )
    conn.commit()
    conn.close()

def delete_product(product_id):
    conn = get_connection()
    if not conn:
        return False, "Connection failed"
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM products WHERE id=%s", (product_id,))
        conn.commit()
        return True, "Deleted"
    except Exception as e:
        return False, "This product has cartons or sales linked to it and cannot be deleted."
    finally:
        conn.close()

def get_dashboard_stats():
    conn = get_connection()
    if not conn:
        return (0, 0, 0, 0)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(quantity) FROM products")
    total_stock = cursor.fetchone()[0] or 0
    cursor.execute("SELECT COUNT(*) FROM products WHERE quantity <= 10")
    low_stock = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(quantity * price) FROM products")
    total_value = cursor.fetchone()[0] or 0
    conn.close()
    return (total_products, total_stock, low_stock, round(total_value, 2))
# ── SALES FUNCTIONS ──
def record_sale(product_id, quantity_sold, total_price):
    conn = get_connection()
    if not conn:
        return None
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sales (product_id, quantity_sold, total_price) VALUES (%s,%s,%s)",
        (product_id, quantity_sold, total_price)
    )
    sale_id = cursor.lastrowid
    cursor.execute(
        "UPDATE products SET quantity = quantity - %s WHERE id=%s",
        (quantity_sold, product_id)
    )
    conn.commit()
    conn.close()
    return sale_id

def get_all_sales():
    conn = get_connection()
    if not conn:
        return []
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.id, p.name, p.category, s.quantity_sold, 
               s.total_price, s.sale_date
        FROM sales s
        JOIN products p ON s.product_id = p.id
        ORDER BY s.sale_date DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_products_for_sale():
    conn = get_connection()
    if not conn:
        return []
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, category, price, quantity FROM products WHERE quantity > 0")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_sales_stats():
    conn = get_connection()
    if not conn:
        return (0, 0, 0)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sales")
    total_sales = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(total_price) FROM sales")
    total_revenue = cursor.fetchone()[0] or 0
    cursor.execute("SELECT SUM(quantity_sold) FROM sales")
    total_items = cursor.fetchone()[0] or 0
    conn.close()
    return (total_sales, round(total_revenue, 2), total_items)
# ── REPORTS FUNCTIONS ──
def get_top_products(limit=5):
    conn = get_connection()
    if not conn:
        return []
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.name, SUM(s.quantity_sold) AS total_qty, SUM(s.total_price) AS total_revenue
        FROM sales s
        JOIN products p ON s.product_id = p.id
        GROUP BY p.id, p.name
        ORDER BY total_revenue DESC
        LIMIT %s
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_revenue_last_7_days():
    conn = get_connection()
    if not conn:
        return []
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DATE(sale_date) AS day, SUM(total_price) AS revenue
        FROM sales
        WHERE sale_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        GROUP BY DATE(sale_date)
        ORDER BY day
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_full_sales_summary():
    conn = get_connection()
    if not conn:
        return []
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.name, p.category, SUM(s.quantity_sold) AS qty_sold, SUM(s.total_price) AS revenue
        FROM sales s
        JOIN products p ON s.product_id = p.id
        GROUP BY p.id, p.name, p.category
        ORDER BY revenue DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows
# ── SIGN UP FUNCTION ──
def register_user(username, password, email):
    conn = get_connection()
    if not conn:
        return False
    cursor = conn.cursor()
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    cursor.execute(
        "INSERT INTO users (username, password, email) VALUES (%s,%s,%s)",
        (username, hashed, email)
    )
    conn.commit()
    conn.close()
    return True
# ── USER INFO FUNCTION ──
def get_user_info(username):
    conn = get_connection()
    if not conn:
        return None
    cursor = conn.cursor()
    cursor.execute("SELECT username, email, created_at FROM users WHERE username=%s", (username,))
    result = cursor.fetchone()
    conn.close()
    return result

def get_sale_by_id(sale_id):
    conn = get_connection()
    if not conn:
        return None
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.id, p.name, p.category, s.quantity_sold, s.total_price, s.sale_date
        FROM sales s
        JOIN products p ON s.product_id = p.id
        WHERE s.id = %s
    """, (sale_id,))
    row = cursor.fetchone()
    conn.close()
    return row
# ── BARCODE / CARTON FUNCTIONS ──

def set_product_barcode(product_id, barcode_value):
    conn = get_connection()
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET barcode=%s WHERE id=%s", (barcode_value, product_id))
    conn.commit()
    conn.close()

def get_product_by_barcode(barcode_value):
    conn = get_connection()
    if not conn:
        return None
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE barcode=%s", (barcode_value,))
    row = cursor.fetchone()
    conn.close()
    return row

def create_carton(product_id, carton_barcode, units_per_carton):
    conn = get_connection()
    if not conn:
        return None
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO cartons (product_id, carton_barcode, units_per_carton, status) VALUES (%s,%s,%s,%s)",
        (product_id, carton_barcode, units_per_carton, "pending")
    )
    carton_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return carton_id

def get_carton_by_barcode(carton_barcode):
    conn = get_connection()
    if not conn:
        return None
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, c.product_id, p.name, c.carton_barcode, c.units_per_carton, c.status
        FROM cartons c
        JOIN products p ON c.product_id = p.id
        WHERE c.carton_barcode=%s
    """, (carton_barcode,))
    row = cursor.fetchone()
    conn.close()
    return row

def add_location(name, location_code):
    conn = get_connection()
    if not conn:
        return None
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO locations (name, location_code) VALUES (%s,%s)",
        (name, location_code)
    )
    loc_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return loc_id

def get_location_by_code(location_code):
    conn = get_connection()
    if not conn:
        return None
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM locations WHERE location_code=%s", (location_code,))
    row = cursor.fetchone()
    conn.close()
    return row

def log_movement(carton_id, location_id, action):
    conn = get_connection()
    if not conn:
        return
    cursor = conn.cursor()

    # Get carton's current status BEFORE this scan, plus product_id and units
    cursor.execute("SELECT product_id, units_per_carton, status FROM cartons WHERE id=%s", (carton_id,))
    carton_info = cursor.fetchone()

    cursor.execute(
        "INSERT INTO stock_movements (carton_id, location_id, action) VALUES (%s,%s,%s)",
        (carton_id, location_id, action)
    )

    if carton_info:
        product_id, units_per_carton, previous_status = carton_info

        # Only add stock the FIRST time a carton is marked received
        # (prevents double-counting if someone scans "received" twice by mistake)
        if action == "received" and previous_status != "received":
            cursor.execute(
                "UPDATE products SET quantity = quantity + %s WHERE id=%s",
                (units_per_carton, product_id)
            )

        cursor.execute("UPDATE cartons SET status=%s WHERE id=%s", (action if action != "moved" else "stored", carton_id))

    conn.commit()
    conn.close()

def get_movement_history(carton_id):
    conn = get_connection()
    if not conn:
        return []
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sm.id, l.name, sm.action, sm.scanned_at
        FROM stock_movements sm
        LEFT JOIN locations l ON sm.location_id = l.id
        WHERE sm.carton_id=%s
        ORDER BY sm.scanned_at DESC
    """, (carton_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

