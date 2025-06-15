import sqlite3

# Initialize database connection
def init_db():
    conn = sqlite3.connect("business.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        percentage REAL,
        image_path TEXT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        total REAL,
        payment_type TEXT,
        date TEXT,
        FOREIGN KEY(client_id) REFERENCES clients(id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS representatives (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        establishment TEXT,
        contact TEXT
    )''')
    conn.commit()
    conn.close()

# Clients
def add_client(name, email, phone):
    if not name:
        return False
    conn = sqlite3.connect("business.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clients (name, email, phone) VALUES (?, ?, ?)", (name, email, phone))
    conn.commit()
    conn.close()
    return True

def edit_client(client_id, name, email, phone):
    if not name:
        return False
    conn = sqlite3.connect("business.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE clients SET name=?, email=?, phone=? WHERE id=?", (name, email, phone, client_id))
    conn.commit()
    conn.close()
    return True

def delete_client(client_id):
    conn = sqlite3.connect("business.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clients WHERE id=?", (client_id,))
    conn.commit()
    conn.close()
    return True

def get_client(client_id):
    conn = sqlite3.connect("business.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients WHERE id=?", (client_id,))
    client = cursor.fetchone()
    conn.close()
    return client

def get_all_clients():
    conn = sqlite3.connect("business.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, phone FROM clients")
    clients = cursor.fetchall()
    conn.close()
    return clients

# Products
def add_product(name, price, percentage, image_path):
    if not name or not price:
        return False
    conn = sqlite3.connect("business.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, price, percentage, image_path) VALUES (?, ?, ?, ?)",
                   (name, price, percentage, image_path))
    conn.commit()
    conn.close()
    return True

def edit_product(product_id, name, price, percentage, image_path):
    if not name or not price:
        return False
    conn = sqlite3.connect("business.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET name=?, price=?, percentage=?, image_path=? WHERE id=?",
                   (name, price, percentage, image_path, product_id))
    conn.commit()
    conn.close()
    return True

def delete_product(product_id):
    conn = sqlite3.connect("business.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()
    return True

def get_product(product_id):
    conn = sqlite3.connect("business.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id=?", (product_id,))
    product = cursor.fetchone()
    conn.close()
    return product

def get_product_price(product_id):
    conn = sqlite3.connect("business.db")
    cursor = conn.cursor()
    cursor.execute("SELECT price FROM products WHERE id=?", (product_id,))
    price = cursor.fetchone()[0]
    conn.close()
    return price

def get_all_products():
    conn = sqlite3.connect("business.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price, percentage FROM products")
    products = cursor.fetchall()
    conn.close()
    return products

# Orders
def add_sale(client_id, product_id, quantity, total, payment_type):
    conn = sqlite3.connect("business.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders (client_id, product_id, quantity, total, payment_type, date) VALUES (?, ?, ?, ?, ?, ?)",
                   (client_id, product_id, quantity, total, payment_type, datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()
    return True

def get_sale(order_id):
    conn = sqlite3.connect("business.db")
    cursor = conn.cursor()
    cursor.execute('''SELECT orders.id, clients.name, products.name, orders.quantity, orders.total, orders.payment_type
                      FROM orders
                      JOIN clients ON orders.client_id = clients.id
                      JOIN products ON orders.product_id = products.id
                      WHERE orders.id = ?''', (order_id,))
    sale = cursor.fetchone()
    conn.close()
    return sale

def get_all_sales():
    conn = sqlite3.connect("business.db")
    cursor = conn.cursor()
    cursor.execute('''SELECT orders.id, clients.name, products.name, orders.quantity, orders.total, orders.payment_type
                      FROM orders
                      JOIN clients ON orders.client_id = clients.id
                      JOIN products ON orders.product_id = products.id''')
    sales = cursor.fetchall()
    conn.close()
    return sales

# Representatives
def add_representative(name, establishment, contact):
    if not name:
        return False
    conn = sqlite3.connect("business.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO representatives (name, establishment, contact) VALUES (?, ?, ?)", (name, establishment, contact))
    conn.commit()
    conn.close()
    return True

def edit_representative(rep_id, name, establishment, contact):
    if not name:
        return False
    conn = sqlite3.connect("business.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE representatives SET name=?, establishment=?, contact=? WHERE id=?", (name, establishment, contact, rep_id))
    conn.commit()
    conn.close()
    return True

def delete_representative(rep_id):
    conn = sqlite3.connect("business.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM representatives WHERE id=?", (rep_id,))
    conn.commit()
    conn.close()
    return True

def get_representative(rep_id):
    conn = sqlite3.connect("business.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM representatives WHERE id=?", (rep_id,))
    rep = cursor.fetchone()
    conn.close()
    return rep

def get_all_representatives():
    conn = sqlite3.connect("business.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, establishment, contact FROM representatives")
    reps = cursor.fetchall()
    conn.close()
    return reps