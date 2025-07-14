import sqlite3
from flask import Flask, request, jsonify, g, Response
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

DATABASE = "tashmall.db"
TELEGRAM_BOT_TOKEN = "7779332599:AAFQ6K9GpYmKSoHwq8F3BmUrDGDOs9yAmyk"  # <-- ВСТАВЬ сюда свой токен!

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        c = db.cursor()
        # users
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                name TEXT UNIQUE,
                role TEXT,
                password TEXT
            )
        """)
        # shops
        c.execute("""
            CREATE TABLE IF NOT EXISTS shops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_telegram_id INTEGER,
                name TEXT
            )
        """)
        # products
        c.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                shop_id INTEGER,
                name TEXT,
                price REAL,
                description TEXT,
                photo_file_id TEXT
            )
        """)
        # orders
        c.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                buyer_id INTEGER,
                shop_id INTEGER,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # order_items
        c.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                product_id INTEGER,
                qty INTEGER,
                price_snapshot REAL
            )
        """)
        db.commit()

# USERS API
@app.route("/api/user/<int:telegram_id>", methods=["GET"])
def get_users_by_telegram_id(telegram_id):
    db = get_db()
    rows = db.execute("SELECT * FROM users WHERE telegram_id=?", (telegram_id,)).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/user_by_username/<username>", methods=["GET"])
def get_user_by_username(username):
    db = get_db()
    row = db.execute("SELECT * FROM users WHERE name=?", (username,)).fetchone()
    if row:
        return jsonify(dict(row))
    return jsonify({}), 404

@app.route("/api/user", methods=["POST"])
def create_user():
    data = request.json
    telegram_id = data["telegram_id"]
    name = data["name"]
    role = data["role"]
    password = data["password"]
    db = get_db()

    # Лимит аккаунтов
    count = db.execute("SELECT COUNT(*) FROM users WHERE telegram_id=?", (telegram_id,)).fetchone()[0]
    if count >= 3:
        return jsonify({"error": "account limit"}), 400
    # Уникальность имени
    exists = db.execute("SELECT 1 FROM users WHERE name=?", (name,)).fetchone()
    if exists:
        return jsonify({"error": "name taken"}), 400

    db.execute(
        "INSERT INTO users (telegram_id, name, role, password) VALUES (?, ?, ?, ?)",
        (telegram_id, name, role, password)
    )
    db.commit()
    return jsonify({"success": True}), 201

@app.route("/api/user/<int:telegram_id>", methods=["DELETE"])
def delete_users_by_telegram_id(telegram_id):
    db = get_db()
    db.execute("DELETE FROM users WHERE telegram_id=?", (telegram_id,))
    db.commit()
    return "", 204

@app.route("/api/user_by_username/<username>", methods=["DELETE"])
def delete_user_by_username(username):
    db = get_db()
    db.execute("DELETE FROM users WHERE name=?", (username,))
    db.commit()
    return "", 204

# SHOPS API
@app.route("/api/shops", methods=["GET"])
def get_shops():
    db = get_db()
    rows = db.execute("SELECT * FROM shops").fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/shops", methods=["POST"])
def create_shop():
    data = request.json
    owner_telegram_id = data["owner_telegram_id"]
    name = data["name"]
    db = get_db()
    db.execute(
        "INSERT INTO shops (owner_telegram_id, name) VALUES (?, ?)",
        (owner_telegram_id, name)
    )
    db.commit()
    return jsonify({"success": True}), 201

@app.route("/api/shops/<int:shop_id>", methods=["DELETE"])
def delete_shop(shop_id):
    db = get_db()
    db.execute("DELETE FROM shops WHERE id=?", (shop_id,))
    db.commit()
    return "", 204

# PRODUCTS API
@app.route("/api/products/<int:shop_id>", methods=["GET"])
def get_products(shop_id):
    db = get_db()
    rows = db.execute("SELECT * FROM products WHERE shop_id=?", (shop_id,)).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/products", methods=["POST"])
def add_product():
    data = request.json
    shop_id = data["shop_id"]
    name = data["name"]
    price = data["price"]
    description = data["description"]
    photo_file_id = data.get("photo_file_id")
    db = get_db()
    db.execute(
        "INSERT INTO products (shop_id, name, price, description, photo_file_id) VALUES (?, ?, ?, ?, ?)",
        (shop_id, name, price, description, photo_file_id)
    )
    db.commit()
    return jsonify({"success": True}), 201

@app.route("/api/products", methods=["GET"])
def get_products_query():
    shop_id = request.args.get("shop_id")
    db = get_db()
    if shop_id:
        rows = db.execute("SELECT * FROM products WHERE shop_id=?", (shop_id,)).fetchall()
    else:
        rows = db.execute("SELECT * FROM products").fetchall()
    return jsonify([dict(r) for r in rows])

# === Новый эндпоинт для отдачи фото Telegram по file_id ===
@app.route("/api/photo_telegram/<file_id>", methods=["GET"])
def proxy_telegram_photo(file_id):
    # 1. Получить путь к файлу через Telegram API
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile?file_id={file_id}"
    resp = requests.get(url)
    result = resp.json()
    if not result.get("ok"):
        return jsonify({"error": "file not found in Telegram"}), 404
    file_path = result["result"]["file_path"]
    # 2. Скачать файл с серверов Telegram
    file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
    file_resp = requests.get(file_url, stream=True)
    if file_resp.status_code != 200:
        return jsonify({"error": "file download failed"}), 404
    mimetype = file_resp.headers.get("Content-Type", "image/jpeg")
    return Response(file_resp.content, mimetype=mimetype)

# Старый эндпоинт (не используется для фото на сайте)
@app.route("/api/photo/<photo_file_id>", methods=["GET"])
def get_product_photo(photo_file_id):
    db = get_db()
    row = db.execute("SELECT * FROM products WHERE photo_file_id=?", (photo_file_id,)).fetchone()
    if not row:
        return jsonify({"error": "not found"}), 404
    return jsonify({"photo_file_id": photo_file_id})

# ========== ORDERS API ==========

@app.route("/api/orders", methods=["POST"])
def create_order():
    data = request.json
    buyer_id = data["buyer_id"]
    shop_id = data["shop_id"]
    items = data["items"]  # [{product_id, qty, price_snapshot}]
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO orders (buyer_id, shop_id, status) VALUES (?, ?, ?)",
        (buyer_id, shop_id, "новый")
    )
    order_id = cur.lastrowid
    for item in items:
        cur.execute(
            "INSERT INTO order_items (order_id, product_id, qty, price_snapshot) VALUES (?, ?, ?, ?)",
            (order_id, item["product_id"], item["qty"], item["price_snapshot"])
        )
    db.commit()
    return jsonify({"success": True, "order_id": order_id}), 201

@app.route("/api/orders/<int:buyer_id>", methods=["GET"])
def get_orders_by_buyer(buyer_id):
    db = get_db()
    orders = db.execute(
        "SELECT * FROM orders WHERE buyer_id=? ORDER BY created_at DESC", (buyer_id,)
    ).fetchall()
    result = []
    for order in orders:
        items = db.execute(
            "SELECT oi.*, p.name, p.photo_file_id FROM order_items oi LEFT JOIN products p ON oi.product_id=p.id WHERE oi.order_id=?",
            (order["id"],)
        ).fetchall()
        result.append({
            "order": dict(order),
            "items": [dict(i) for i in items]
        })
    return jsonify(result)

@app.route("/api/shop_orders/<int:shop_id>", methods=["GET"])
def get_orders_by_shop(shop_id):
    db = get_db()
    orders = db.execute(
        "SELECT * FROM orders WHERE shop_id=? ORDER BY created_at DESC", (shop_id,)
    ).fetchall()
    result = []
    for order in orders:
        items = db.execute(
            "SELECT oi.*, p.name, p.photo_file_id FROM order_items oi LEFT JOIN products p ON oi.product_id=p.id WHERE oi.order_id=?",
            (order["id"],)
        ).fetchall()
        result.append({
            "order": dict(order),
            "items": [dict(i) for i in items]
        })
    return jsonify(result)

@app.route("/api/orders/<int:order_id>/status", methods=["PATCH"])
def update_order_status(order_id):
    data = request.json
    status = data["status"]
    db = get_db()
    db.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
    db.commit()
    return jsonify({"success": True})

# ========== CHECKOUT API ===========
@app.route("/api/checkout", methods=["POST"])
def checkout():
    data = request.json
    buyer_id = data["buyer_id"]
    cart_items = data["items"]  # [{product_id, qty}]
    db = get_db()
    cur = db.cursor()

    # Получаем информацию о товарах и магазинах
    product_map = {}
    shop_map = {}
    for item in cart_items:
        product = db.execute(
            "SELECT * FROM products WHERE id=?",
            (item["product_id"],)
        ).fetchone()
        if not product:
            return jsonify({"error": f"Product {item['product_id']} not found"}), 400
        product_map[item["product_id"]] = product
        shop_id = product["shop_id"]
        shop_map.setdefault(shop_id, []).append({
            "product_id": item["product_id"],
            "qty": item["qty"],
            "price_snapshot": product["price"]
        })

    results = []
    for shop_id, items in shop_map.items():
        # Создаем заказ
        cur.execute(
            "INSERT INTO orders (buyer_id, shop_id, status) VALUES (?, ?, ?)",
            (buyer_id, shop_id, "новый")
        )
        order_id = cur.lastrowid
        # Добавляем товары в заказ
        for item in items:
            cur.execute(
                "INSERT INTO order_items (order_id, product_id, qty, price_snapshot) VALUES (?, ?, ?, ?)",
                (order_id, item["product_id"], item["qty"], item["price_snapshot"])
            )
        # Считаем итоговую сумму заказа
        total = sum(item["qty"] * item["price_snapshot"] for item in items)
        # Получаем данные магазина
        shop = db.execute("SELECT * FROM shops WHERE id=?", (shop_id,)).fetchone()
        results.append({
            "order_id": order_id,
            "shop_id": shop_id,
            "shop_name": shop["name"] if shop else None,
            "total": total
        })
    db.commit()
    # После успешного оформления корзину на стороне бота нужно очистить вручную
    return jsonify({"success": True, "orders": results}), 201

if __name__ == "__main__":
    init_db()
    app.run(port=8000, debug=True)