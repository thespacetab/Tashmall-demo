import sqlite3

def init_db():
    conn = sqlite3.connect("tashmall.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            name TEXT,
            role TEXT CHECK(role IN ('buyer', 'seller'))
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS shops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_telegram_id INTEGER,
            name TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_id INTEGER,
            name TEXT,
            price REAL,
            description TEXT
        )
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("База данных tashmall.db инициализирована!")