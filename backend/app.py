from flask import Flask, jsonify, request
import sqlite3
from flask_cors import CORS
import bcrypt

app = Flask(__name__)
CORS(app)

def get_db():
    conn = sqlite3.connect("tashmall.db")
    conn.row_factory = sqlite3.Row
    return conn

# --- USERS ---

@app.route("/api/user/<int:telegram_id>", methods=["GET"])
def get_user_by_telegram_id(telegram_id):
    conn = get_db()
    users = conn.execute("SELECT * FROM users WHERE telegram_id=?", (telegram_id,)).fetchall()
    conn.close()
    if users:
        return jsonify([dict(u) for u in users])
    return jsonify([]), 404

@app.route("/api/user_by_username/<username>", methods=["GET"])
def get_user_by_username(username):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE name=?", (username,)).fetchone()
    conn.close()
    if user:
        return jsonify(dict(user))
    return jsonify({}), 404

@app.route("/api/user", methods=["POST"])
def create_user():
    data = request.json
    print("DEBUG: Получены данные для регистрации:", data)
    required_fields = ["telegram_id", "name", "role", "password"]
    for field in required_fields:
        if not data.get(field):
            print(f"DEBUG: Нет поля {field} или оно пустое")
            return jsonify({"error": f"Missing or empty field: {field}"}), 400

    conn = get_db()
    count = conn.execute(
        "SELECT COUNT(*) FROM users WHERE telegram_id=?",
        (data["telegram_id"],)
    ).fetchone()[0]
    if count >= 3:
        print("DEBUG: Превышено количество аккаунтов для этого telegram_id")
        conn.close()
        return jsonify({"error": "You can have no more than 3 accounts for this Telegram ID"}), 409

    existing = conn.execute(
        "SELECT id FROM users WHERE name=?",
        (data["name"],)
    ).fetchone()
    if existing:
        print("DEBUG: Пользователь с таким именем уже есть")
        conn.close()
        return jsonify({"error": "Username already exists"}), 409

    try:
        conn.execute(
            "INSERT INTO users (telegram_id, name, role, password) VALUES (?, ?, ?, ?)",
            (data["telegram_id"], data["name"], data["role"], data["password"])
        )
        conn.commit()
        print("DEBUG: Пользователь успешно создан")
        return '', 201
    except Exception as e:
        print("DEBUG: Неизвестная ошибка при записи в БД:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route("/api/user/<int:telegram_id>", methods=["DELETE"])
def delete_user(telegram_id):
    conn = get_db()
    try:
        conn.execute("DELETE FROM users WHERE telegram_id=?", (telegram_id,))
        conn.commit()
        return '', 204
    finally:
        conn.close()

# --- SHOPS ---

@app.route("/api/shops", methods=["GET"])
def get_shops():
    owner_telegram_id = request.args.get("owner_telegram_id")
    conn = get_db()
    if owner_telegram_id:
        rows = conn.execute("SELECT * FROM shops WHERE owner_telegram_id=?", (owner_telegram_id,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM shops").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/shops", methods=["POST"])
def create_shop():
    data = request.json
    conn = get_db()
    try:
        conn.execute("INSERT INTO shops (owner_telegram_id, name) VALUES (?, ?)",
                     (data["owner_telegram_id"], data["name"]))
        conn.commit()
        return '', 201
    finally:
        conn.close()

# --- PRODUCTS ---
@app.route("/api/products/<int:shop_id>", methods=["GET"])
def get_products(shop_id):
    conn = get_db()
    rows = conn.execute("SELECT * FROM products WHERE shop_id=?", (shop_id,)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/products", methods=["POST"])
def create_product():
    data = request.json
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO products (shop_id, name, price, description) VALUES (?, ?, ?, ?)",
            (data["shop_id"], data["name"], data["price"], data["description"])
        )
        conn.commit()
        return '', 201
    finally:
        conn.close()

# --- DB INIT ---
def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            name TEXT UNIQUE,
            role TEXT CHECK(role IN ('buyer', 'seller')),
            password TEXT
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
    app.run(port=8000, debug=True)