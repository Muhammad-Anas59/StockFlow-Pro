# database.py
import mysql.connector
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
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    result = cursor.fetchone()
    conn.close()
    return result is not None

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
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password=%s WHERE username=%s", (new_password, username))
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

def delete_product(pid):
    conn = get_connection()
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=%s", (pid,))
    conn.commit()
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
        return False
    cursor = conn.cursor()
    # Record the sale
    cursor.execute(
        "INSERT INTO sales (product_id, quantity_sold, total_price) VALUES (%s,%s,%s)",
        (product_id, quantity_sold, total_price)
    )
    # Reduce stock
    cursor.execute(
        "UPDATE products SET quantity = quantity - %s WHERE id=%s",
        (quantity_sold, product_id)
    )
    conn.commit()
    conn.close()
    return True

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
    cursor.execute("SELECT id, name, price, quantity FROM products WHERE quantity > 0")
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
    cursor.execute(
        "INSERT INTO users (username, password, email) VALUES (%s,%s,%s)",
        (username, password, email)
    )
    conn.commit()
    conn.close()
    return True