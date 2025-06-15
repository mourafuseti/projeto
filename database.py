import sqlite3
import bcrypt


def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    # Criar tabela users se não existir
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            name TEXT,
            email TEXT,
            phone TEXT
        )
    ''')
    # Adicionar colunas address e city se não existirem
    columns = [col['name'] for col in conn.execute('PRAGMA table_info(users)').fetchall()]
    if 'address' not in columns:
        conn.execute('ALTER TABLE users ADD COLUMN address TEXT')
    if 'city' not in columns:
        conn.execute('ALTER TABLE users ADD COLUMN city TEXT')

    # Criar outras tabelas
    conn.execute('''
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            description TEXT,
            photo TEXT,
            days_of_week TEXT,
            FOREIGN KEY (student_id) REFERENCES users (id)
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            amount REAL,
            due_date TEXT,
            pix_key TEXT,
            qr_code TEXT,
            receipt TEXT,
            FOREIGN KEY (student_id) REFERENCES users (id)
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER,
            receiver_id INTEGER,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users (id),
            FOREIGN KEY (receiver_id) REFERENCES users (id)
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS body_measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            weight REAL NOT NULL,
            height REAL NOT NULL,
            imc REAL NOT NULL,
            measured_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users (id)
        )
    ''')
    # Criar usuário admin padrão se não existir
    admin_password = 'admin123'.encode('utf-8')
    hashed_password = bcrypt.hashpw(admin_password, bcrypt.gensalt()).decode('utf-8')
    conn.execute(
        'INSERT OR IGNORE INTO users (username, password, role, name, email, phone, address, city) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        ('admin', hashed_password, 'admin', 'Administrador', 'admin@gym.com', '123456789', 'Rua Admin', 'Cidade Admin'))
    conn.commit()
    conn.close()