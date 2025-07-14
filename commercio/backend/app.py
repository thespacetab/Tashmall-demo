import sqlite3
from flask import Flask, request, jsonify, g, Response
from flask_cors import CORS
import requests
from datetime import datetime, timedelta
import json

app = Flask(__name__)
CORS(app)

DATABASE = "commercio.db"
TELEGRAM_BOT_TOKEN = "7779332599:AAFQ6K9GpYmKSoHwq8F3BmUrDGDOs9yAmyk"

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
        
        # Users table
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                name TEXT UNIQUE,
                email TEXT,
                phone TEXT,
                role TEXT,
                password TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # Shops table
        c.execute("""
            CREATE TABLE IF NOT EXISTS shops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_telegram_id INTEGER,
                name TEXT,
                description TEXT,
                category TEXT,
                logo_file_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # Products table
        c.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                shop_id INTEGER,
                name TEXT,
                price REAL,
                description TEXT,
                photo_file_id TEXT,
                category TEXT,
                stock INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # Events table
        c.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT,
                category TEXT,
                date TEXT,
                time TEXT,
                location TEXT,
                organizer_id INTEGER,
                organizer_name TEXT,
                price REAL DEFAULT 0,
                max_attendees INTEGER,
                current_attendees INTEGER DEFAULT 0,
                status TEXT DEFAULT 'upcoming',
                image_icon TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Event registrations table
        c.execute("""
            CREATE TABLE IF NOT EXISTS event_registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER,
                user_id INTEGER,
                user_name TEXT,
                user_email TEXT,
                user_phone TEXT,
                user_company TEXT,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'confirmed'
            )
        """)
        
        # Partners table
        c.execute("""
            CREATE TABLE IF NOT EXISTS partners (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                role TEXT,
                company TEXT,
                avatar_icon TEXT,
                projects_count INTEGER DEFAULT 0,
                revenue REAL DEFAULT 0,
                telegram_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # Orders table
        c.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                buyer_id INTEGER,
                shop_id INTEGER,
                status TEXT,
                total_amount REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Order items table
        c.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                product_id INTEGER,
                qty INTEGER,
                price_snapshot REAL
            )
        """)
        
        # Referral system table
        c.execute("""
            CREATE TABLE IF NOT EXISTS referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER,
                referred_id INTEGER,
                status TEXT DEFAULT 'pending',
                commission_earned REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    telegram_id = data.get("telegram_id", 0)
    name = data["name"]
    role = data["role"]
    password = data["password"]
    email = data.get("email", "")
    phone = data.get("phone", "")
    
    db = get_db()

    # Check account limit
    count = db.execute("SELECT COUNT(*) FROM users WHERE telegram_id=?", (telegram_id,)).fetchone()[0]
    if count >= 3:
        return jsonify({"error": "account limit"}), 400
    
    # Check name uniqueness
    exists = db.execute("SELECT 1 FROM users WHERE name=?", (name,)).fetchone()
    if exists:
        return jsonify({"error": "name taken"}), 400

    db.execute(
        "INSERT INTO users (telegram_id, name, email, phone, role, password) VALUES (?, ?, ?, ?, ?, ?)",
        (telegram_id, name, email, phone, role, password)
    )
    db.commit()
    return jsonify({"success": True}), 201

@app.route("/api/user/<int:telegram_id>", methods=["DELETE"])
def delete_users_by_telegram_id(telegram_id):
    db = get_db()
    db.execute("DELETE FROM users WHERE telegram_id=?", (telegram_id,))
    db.commit()
    return "", 204

# SHOPS API
@app.route("/api/shops", methods=["GET"])
def get_shops():
    db = get_db()
    rows = db.execute("SELECT * FROM shops WHERE is_active=1").fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/shops", methods=["POST"])
def create_shop():
    data = request.json
    owner_telegram_id = data["owner_telegram_id"]
    name = data["name"]
    description = data.get("description", "")
    category = data.get("category", "general")
    logo_file_id = data.get("logo_file_id")
    
    db = get_db()
    db.execute(
        "INSERT INTO shops (owner_telegram_id, name, description, category, logo_file_id) VALUES (?, ?, ?, ?, ?)",
        (owner_telegram_id, name, description, category, logo_file_id)
    )
    db.commit()
    return jsonify({"success": True}), 201

@app.route("/api/shops/<int:shop_id>", methods=["DELETE"])
def delete_shop(shop_id):
    db = get_db()
    db.execute("UPDATE shops SET is_active=0 WHERE id=?", (shop_id,))
    db.commit()
    return "", 204

# PRODUCTS API
@app.route("/api/products/<int:shop_id>", methods=["GET"])
def get_products(shop_id):
    db = get_db()
    rows = db.execute("SELECT * FROM products WHERE shop_id=? AND is_active=1", (shop_id,)).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/products", methods=["POST"])
def add_product():
    data = request.json
    shop_id = data["shop_id"]
    name = data["name"]
    price = data["price"]
    description = data.get("description", "")
    photo_file_id = data.get("photo_file_id")
    category = data.get("category", "general")
    stock = data.get("stock", 0)
    
    db = get_db()
    db.execute(
        "INSERT INTO products (shop_id, name, price, description, photo_file_id, category, stock) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (shop_id, name, price, description, photo_file_id, category, stock)
    )
    db.commit()
    return jsonify({"success": True}), 201

@app.route("/api/products", methods=["GET"])
def get_products_query():
    shop_id = request.args.get("shop_id")
    db = get_db()
    if shop_id:
        rows = db.execute("SELECT * FROM products WHERE shop_id=? AND is_active=1", (shop_id,)).fetchall()
    else:
        rows = db.execute("SELECT * FROM products WHERE is_active=1").fetchall()
    return jsonify([dict(r) for r in rows])

# EVENTS API
@app.route("/api/events", methods=["GET"])
def get_events():
    db = get_db()
    category = request.args.get("category")
    status = request.args.get("status")
    date = request.args.get("date")
    
    query = "SELECT * FROM events WHERE 1=1"
    params = []
    
    if category:
        query += " AND category=?"
        params.append(category)
    
    if status:
        query += " AND status=?"
        params.append(status)
    
    if date:
        query += " AND date=?"
        params.append(date)
    
    query += " ORDER BY date ASC, time ASC"
    
    rows = db.execute(query, params).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/events", methods=["POST"])
def create_event():
    data = request.json
    title = data["title"]
    description = data["description"]
    category = data["category"]
    date = data["date"]
    time = data["time"]
    location = data["location"]
    organizer_id = data.get("organizer_id")
    organizer_name = data["organizer_name"]
    price = data.get("price", 0)
    max_attendees = data["max_attendees"]
    image_icon = data.get("image_icon", "fas fa-calendar")
    tags = json.dumps(data.get("tags", []))
    
    db = get_db()
    db.execute(
        """INSERT INTO events (title, description, category, date, time, location, 
           organizer_id, organizer_name, price, max_attendees, image_icon, tags) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (title, description, category, date, time, location, organizer_id, 
         organizer_name, price, max_attendees, image_icon, tags)
    )
    db.commit()
    return jsonify({"success": True}), 201

@app.route("/api/events/<int:event_id>", methods=["GET"])
def get_event(event_id):
    db = get_db()
    row = db.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
    if row:
        event = dict(row)
        event['tags'] = json.loads(event.get('tags', '[]'))
        return jsonify(event)
    return jsonify({}), 404

@app.route("/api/events/<int:event_id>/register", methods=["POST"])
def register_for_event(event_id):
    data = request.json
    user_id = data.get("user_id")
    user_name = data["user_name"]
    user_email = data["user_email"]
    user_phone = data["user_phone"]
    user_company = data.get("user_company", "")
    
    db = get_db()
    
    # Check if event exists and has available spots
    event = db.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
    if not event:
        return jsonify({"error": "Event not found"}), 404
    
    if event['current_attendees'] >= event['max_attendees']:
        return jsonify({"error": "Event is full"}), 400
    
    # Check if user is already registered
    existing = db.execute("SELECT 1 FROM event_registrations WHERE event_id=? AND user_email=?", 
                         (event_id, user_email)).fetchone()
    if existing:
        return jsonify({"error": "Already registered"}), 400
    
    # Register user
    db.execute(
        """INSERT INTO event_registrations (event_id, user_id, user_name, user_email, user_phone, user_company) 
           VALUES (?, ?, ?, ?, ?, ?)""",
        (event_id, user_id, user_name, user_email, user_phone, user_company)
    )
    
    # Update event attendees count
    db.execute("UPDATE events SET current_attendees = current_attendees + 1 WHERE id=?", (event_id,))
    
    db.commit()
    return jsonify({"success": True}), 201

# PARTNERS API
@app.route("/api/partners", methods=["GET"])
def get_partners():
    db = get_db()
    rows = db.execute("SELECT * FROM partners WHERE is_active=1").fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/partners", methods=["POST"])
def create_partner():
    data = request.json
    name = data["name"]
    role = data["role"]
    company = data.get("company", "")
    avatar_icon = data.get("avatar_icon", "fas fa-user")
    projects_count = data.get("projects_count", 0)
    revenue = data.get("revenue", 0)
    telegram_id = data.get("telegram_id")
    
    db = get_db()
    db.execute(
        """INSERT INTO partners (name, role, company, avatar_icon, projects_count, revenue, telegram_id) 
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (name, role, company, avatar_icon, projects_count, revenue, telegram_id)
    )
    db.commit()
    return jsonify({"success": True}), 201

# ORDERS API
@app.route("/api/orders", methods=["POST"])
def create_order():
    data = request.json
    buyer_id = data["buyer_id"]
    shop_id = data["shop_id"]
    items = data["items"]
    total_amount = data["total_amount"]
    
    db = get_db()
    
    # Create order
    c = db.execute(
        "INSERT INTO orders (buyer_id, shop_id, status, total_amount) VALUES (?, ?, ?, ?)",
        (buyer_id, shop_id, "pending", total_amount)
    )
    order_id = c.lastrowid
    
    # Add order items
    for item in items:
        db.execute(
            "INSERT INTO order_items (order_id, product_id, qty, price_snapshot) VALUES (?, ?, ?, ?)",
            (order_id, item["product_id"], item["qty"], item["price"])
        )
    
    db.commit()
    return jsonify({"success": True, "order_id": order_id}), 201

@app.route("/api/orders/<int:buyer_id>", methods=["GET"])
def get_orders_by_buyer(buyer_id):
    db = get_db()
    rows = db.execute("""
        SELECT o.*, s.name as shop_name 
        FROM orders o 
        JOIN shops s ON o.shop_id = s.id 
        WHERE o.buyer_id=?
        ORDER BY o.created_at DESC
    """, (buyer_id,)).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/shop_orders/<int:shop_id>", methods=["GET"])
def get_orders_by_shop(shop_id):
    db = get_db()
    rows = db.execute("""
        SELECT o.*, u.name as buyer_name 
        FROM orders o 
        JOIN users u ON o.buyer_id = u.telegram_id 
        WHERE o.shop_id=?
        ORDER BY o.created_at DESC
    """, (shop_id,)).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/orders/<int:order_id>/status", methods=["PATCH"])
def update_order_status(order_id):
    data = request.json
    status = data["status"]
    
    db = get_db()
    db.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
    db.commit()
    return jsonify({"success": True})

# REFERRAL API
@app.route("/api/referrals", methods=["POST"])
def create_referral():
    data = request.json
    referrer_id = data["referrer_id"]
    referred_id = data["referred_id"]
    
    db = get_db()
    db.execute(
        "INSERT INTO referrals (referrer_id, referred_id) VALUES (?, ?)",
        (referrer_id, referred_id)
    )
    db.commit()
    return jsonify({"success": True}), 201

@app.route("/api/referrals/<int:user_id>", methods=["GET"])
def get_user_referrals(user_id):
    db = get_db()
    rows = db.execute("""
        SELECT r.*, u.name as referred_name 
        FROM referrals r 
        JOIN users u ON r.referred_id = u.telegram_id 
        WHERE r.referrer_id=?
    """, (user_id,)).fetchall()
    return jsonify([dict(r) for r in rows])

# Telegram photo proxy
@app.route("/api/photo_telegram/<file_id>", methods=["GET"])
def proxy_telegram_photo(file_id):
    try:
        # Get file path from Telegram
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile?file_id={file_id}"
        resp = requests.get(url)
        result = resp.json()
        
        if not result.get("ok"):
            return jsonify({"error": "File not found"}), 404
        
        file_path = result["result"]["file_path"]
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
        
        # Proxy the file
        file_resp = requests.get(file_url)
        response = Response(file_resp.content)
        response.headers['Content-Type'] = 'image/jpeg'
        return response
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Dashboard statistics
@app.route("/api/dashboard/stats", methods=["GET"])
def get_dashboard_stats():
    db = get_db()
    
    # Get basic stats
    total_users = db.execute("SELECT COUNT(*) FROM users WHERE is_active=1").fetchone()[0]
    total_shops = db.execute("SELECT COUNT(*) FROM shops WHERE is_active=1").fetchone()[0]
    total_products = db.execute("SELECT COUNT(*) FROM products WHERE is_active=1").fetchone()[0]
    total_events = db.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    
    # Get revenue stats
    total_revenue = db.execute("SELECT SUM(total_amount) FROM orders WHERE status='completed'").fetchone()[0] or 0
    
    # Get upcoming events
    upcoming_events = db.execute("""
        SELECT COUNT(*) FROM events 
        WHERE date >= date('now') AND status='upcoming'
    """).fetchone()[0]
    
    return jsonify({
        "total_users": total_users,
        "total_shops": total_shops,
        "total_products": total_products,
        "total_events": total_events,
        "total_revenue": total_revenue,
        "upcoming_events": upcoming_events
    })

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=8000) 