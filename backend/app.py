import os
import json
import random
import psycopg2
from psycopg2 import pool
import traceback
from urllib.parse import urlparse, parse_qs, urlencode
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from werkzeug.security import generate_password_hash, check_password_hash
from google import genai
from ai_helpers import (
    build_order_prompt,
    build_router_prompt,
    build_sales_prompt,
    build_support_prompt,
    classify_route,
    generate_with_gemini,
    local_order_reply,
    local_sales_reply,
    local_support_reply,
)

# ---------------- LOAD ENV ----------------
load_dotenv()

# ---------------- APP CONFIG ----------------
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
from datetime import timedelta

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", os.getenv("JWT_SECRET_KEY", "super-secret-key-for-dev"))
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", app.config["SECRET_KEY"])
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_HEADER_NAME"] = "Authorization"
app.config["JWT_HEADER_TYPE"] = "Bearer"
jwt = JWTManager(app)


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"msg": "Session expired or invalid. Please log in again.", "error": str(error)}), 401


@jwt.unauthorized_loader
def unauthorized_callback(error):
    return jsonify({"msg": "Login required. Please sign in to continue.", "error": str(error)}), 401


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"msg": "Session expired. Please log in again."}), 401

# ---------------- AI CONFIG ----------------
_ai_client = None

def get_ai_client():
    global _ai_client
    if _ai_client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            _ai_client = genai.Client(api_key=api_key)
    return _ai_client

# ---------------- DB CONNECTION (Neon PostgreSQL) ----------------
db_pool = None
resolved_database_url = None


def _clean_database_url(raw_url):
    parsed = urlparse(raw_url)
    if not parsed.scheme:
        return raw_url

    allowed_params = {
        'sslmode', 'connect_timeout', 'application_name', 'fallback_application_name',
        'options', 'sslrootcert', 'sslcert', 'sslkey', 'sslpassword'
    }
    query = parse_qs(parsed.query)
    filtered = {k: v for k, v in query.items() if k in allowed_params}
    cleaned_query = urlencode(filtered, doseq=True)
    return parsed._replace(query=cleaned_query).geturl()


def _connection_candidates():
    candidates = []

    for key in ('POSTGRES_URL', 'DATABASE_URL', 'POSTGRES_URL_NON_POOLING'):
        raw = os.getenv(key, '').strip()
        if raw:
            candidates.append(_clean_database_url(raw))

    host = os.getenv('POSTGRES_HOST', '').strip()
    password = os.getenv('POSTGRES_PASSWORD', '').strip()
    if host and password:
        user = os.getenv('POSTGRES_USER', 'postgres').strip()
        database = os.getenv('POSTGRES_DATABASE', 'postgres').strip()
        candidates.append(
            f"postgresql://{user}:{password}@{host}:5432/{database}?sslmode=require"
        )

    seen = set()
    unique = []
    for url in candidates:
        if url not in seen:
            seen.add(url)
            unique.append(url)
    return unique


def resolve_database_url():
    global resolved_database_url
    if resolved_database_url:
        return resolved_database_url

    candidates = _connection_candidates()
    if not candidates:
        raise RuntimeError(
            'POSTGRES_URL or DATABASE_URL is required. '
            'Add your Neon connection string to backend/.env'
        )

    errors = []
    for url in candidates:
        try:
            conn = psycopg2.connect(url)
            conn.close()
            resolved_database_url = url
            print('PostgreSQL connected successfully')
            return resolved_database_url
        except Exception as exc:
            errors.append(str(exc))

    raise RuntimeError(
        'Could not connect to PostgreSQL. '
        f"Errors: {' | '.join(errors[:2])}"
    )


def get_database_url():
    return resolve_database_url()


def get_pool():
    global db_pool
    if db_pool is None:
        db_pool = pool.ThreadedConnectionPool(1, 10, resolve_database_url())
    return db_pool


def reset_pool():
    global db_pool
    if db_pool is not None:
        try:
            db_pool.closeall()
        except Exception:
            pass
        db_pool = None


def _ping_conn(conn):
    if conn.closed:
        return False
    try:
        conn.rollback()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        return True
    except (psycopg2.OperationalError, psycopg2.InterfaceError):
        return False


def get_conn():
    last_error = None
    for attempt in range(3):
        try:
            conn = get_pool().getconn()
            if _ping_conn(conn):
                return conn
            release_conn(conn, discard=True)
        except (psycopg2.OperationalError, psycopg2.InterfaceError) as exc:
            last_error = exc
            if attempt == 1:
                reset_pool()
    if last_error:
        raise last_error
    raise RuntimeError("Could not acquire a database connection")


def release_conn(conn, discard=False):
    if conn is None:
        return
    try:
        if discard or conn.closed:
            get_pool().putconn(conn, close=True)
        else:
            get_pool().putconn(conn)
    except Exception:
        try:
            conn.close()
        except Exception:
            pass


def execute_query(cur, query, params=None):
    if params is None:
        params = ()
    cur.execute(query.replace('?', '%s'), params)
    return cur


def with_db(callback, retries=2):
    """Run a DB callback with automatic retry on stale connections."""
    last_error = None
    for attempt in range(retries):
        conn = None
        discard = False
        try:
            conn = get_conn()
            cur = conn.cursor()
            result = callback(cur, conn)
            conn.commit()
            return result
        except (psycopg2.OperationalError, psycopg2.InterfaceError) as exc:
            last_error = exc
            discard = True
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            if attempt < retries - 1:
                reset_pool()
                continue
            raise
        except Exception:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            raise
        finally:
            if conn:
                release_conn(conn, discard=discard)
    if last_error:
        raise last_error


# Same catalog as EcommerceSingleAgent (MyStore)
SINGLE_AGENT_PRODUCTS = [
    ("iPhone 15 Pro", 129999, "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=800", "mobiles", "Latest Apple flagship smartphone", 4.8, 520),
    ("Samsung Galaxy S24 Ultra", 119999, "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=800", "mobiles", "Samsung premium AI smartphone", 4.7, 410),
    ("MacBook Air M3", 134999, "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800", "laptops", "Apple M3 ultra fast laptop", 4.9, 380),
    ("ASUS ROG Gaming Laptop", 149999, "https://images.unsplash.com/photo-1593642702821-c8da6771f0c6?w=800", "laptops", "RTX gaming laptop", 4.8, 290),
    ("Sony WH1000XM5", 24999, "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800", "electronics", "Noise cancellation headphones", 4.7, 610),
    ("Nike Air Max", 8999, "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800", "fashion", "Premium sneakers", 4.6, 340),
    ("Luxury Handbag", 4999, "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=800", "fashion", "Elegant designer handbag", 4.5, 180),
    ("Lakme Makeup Kit", 2499, "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=800", "beauty", "Professional beauty makeup kit", 4.4, 220),
    ("Nykaa Face Serum", 999, "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=800", "beauty", "Vitamin C glowing serum", 4.3, 150),
    ("PlayStation 5", 54999, "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=800", "gaming", "Next generation console", 4.9, 890),
]


def seed_single_agent_products(cur):
    for name, price, image, category, description, rating, reviews_count in SINGLE_AGENT_PRODUCTS:
        execute_query(
            cur,
            """
            INSERT INTO products (name, price, image, category, description, rating, reviews_count, specs)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (name, price, image, category, description, rating, reviews_count, "{}"),
        )


def init_db():
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_email TEXT NOT NULL,
            total_amount NUMERIC NOT NULL,
            items TEXT NOT NULL,
            status TEXT DEFAULT 'Paid & Processing',
            payment_method TEXT DEFAULT 'Dummy Card',
            customer_name TEXT,
            shipping_address TEXT,
            tracking_number TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name TEXT,
            price NUMERIC,
            image TEXT,
            category TEXT,
            description TEXT,
            rating NUMERIC DEFAULT 4.5,
            reviews_count INTEGER DEFAULT 100,
            specs TEXT
        );
        """)
        cur.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS customer_name TEXT;")
        cur.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS shipping_address TEXT;")
        cur.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS tracking_number TEXT;")
        cur.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS rating NUMERIC DEFAULT 4.5;")
        cur.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS reviews_count INTEGER DEFAULT 100;")
        cur.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS specs TEXT;")

        cur.execute("SELECT COUNT(*) FROM products;")
        count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM products WHERE name = %s;", ("iPhone 15 Pro",))
        has_single_agent_catalog = cur.fetchone()[0] > 0

        if count == 0 or not has_single_agent_catalog:
            if count > 0:
                print("Replacing product catalog with single-agent products...")
                cur.execute("DELETE FROM products;")
            else:
                print("Seeding products...")
            seed_single_agent_products(cur)
            print("Products seeded successfully.")

        conn.commit()
        cur.close()
    finally:
        release_conn(conn)

init_db()

# ---------------- AUTH ROUTES ----------------
@app.route("/register", methods=["POST"])
def register():
    data = request.json or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"msg": "Missing email or password"}), 400

    hashed = generate_password_hash(password)
    try:
        def db_work(cur, conn):
            execute_query(cur, "INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed))

        with_db(db_work)
        return jsonify({"msg": "Created"}), 201
    except Exception as e:
        err = str(e).lower()
        if 'unique' in err or 'duplicate' in err:
            return jsonify({"msg": "Email already registered"}), 409
        print("Register failed:", repr(e))
        traceback.print_exc()
        return jsonify({"msg": "Server error", "error": str(e)}), 500

@app.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"msg": "Missing email or password"}), 400

    try:
        def db_work(cur, conn):
            execute_query(cur, "SELECT password FROM users WHERE email=?", (email,))
            return cur.fetchone()

        user = with_db(db_work)
        if user and check_password_hash(user[0], password):
            access_token = create_access_token(identity=str(email))
            return jsonify({"access_token": access_token, "email": email}), 200
        return jsonify({"msg": "Invalid email or password"}), 401
    except Exception as e:
        print("Login failed:", repr(e))
        traceback.print_exc()
        return jsonify({"msg": "Server error", "error": str(e)}), 500

@app.route("/auth/verify", methods=["GET"])
@jwt_required()
def verify_auth():
    return jsonify({"email": get_jwt_identity(), "valid": True}), 200

# ---------------- ORDER ROUTES ----------------
@app.route("/orders", methods=["POST"])
@jwt_required()
def place_order():
    user_email = get_jwt_identity()
    data = request.get_json(silent=True) or {}

    items = data.get("items")
    if items is None:
        items = data.get("cart") or data.get("order_items")

    total_amount = data.get("total_amount")
    if total_amount is None:
        total_amount = data.get("totalAmount")

    payment_method = data.get("payment_method") or data.get("paymentMethod") or "Dummy Card"
    customer_name = data.get("customer_name") or data.get("customerName")
    shipping_address = data.get("shipping_address") or data.get("shippingAddress")

    if items is None or total_amount is None:
        print(f"Order payload missing required fields: {data}")
        return jsonify({"msg": "Missing order details", "payload": data}), 400

    if not isinstance(items, list) or len(items) == 0:
        return jsonify({"msg": "Order items must be a non-empty list"}), 400

    conn = get_conn()
    try:
        cur = conn.cursor()
        tracking_number = data.get("tracking_number") or data.get("trackingNumber") or f"TRK{random.randint(100000, 999999)}"
        query = (
            "INSERT INTO orders (user_email, total_amount, items, payment_method, "
            "customer_name, shipping_address, tracking_number) "
            "VALUES (?, ?, ?, ?, ?, ?, ?) RETURNING id"
        )

        execute_query(
            cur,
            query,
            (
                user_email,
                total_amount,
                json.dumps(items),
                payment_method,
                customer_name,
                shipping_address,
                tracking_number,
            ),
        )

        order_id = cur.fetchone()[0]
        conn.commit()
        return jsonify({"msg": "Order placed successfully", "order_id": order_id, "tracking_number": tracking_number}), 201
    except Exception as e:
        conn.rollback()
        print(f"Order placement failed: {e}")
        return jsonify({"msg": "Order failed", "error": str(e)}), 500
    finally:
        release_conn(conn)

@app.route("/orders", methods=["GET"])
@jwt_required()
def get_orders():
    user_email = get_jwt_identity()
    conn = get_conn()
    try:
        cur = conn.cursor()
        execute_query(cur, "SELECT id, total_amount, items, status, created_at, tracking_number, customer_name, shipping_address FROM orders WHERE user_email=?", (user_email,))
        rows = cur.fetchall()
        
        result = []
        for r in rows:
            # r[2] is items string (json)
            try:
                items_obj = json.loads(r[2])
            except:
                items_obj = []
            
            result.append({
                "id": r[0],
                "total": r[1],
                "items": items_obj,
                "status": r[3],
                "date": r[4],
                "tracking_number": r[5] if len(r) > 5 else None,
                "customer_name": r[6] if len(r) > 6 else None,
                "shipping_address": r[7] if len(r) > 7 else None
            })
        return jsonify(result)
    except Exception as e:
        print(f"Get orders failed: {e}")
        return jsonify({"msg": "Could not load orders", "error": str(e)}), 500
    finally:
        release_conn(conn)

# ---------------- PRODUCT ROUTES ----------------
@app.route("/")
def home():
    return "Multi-Agent Backend Running (Neon PostgreSQL)"


@app.route("/db-status")
def db_status():
    try:
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT 1")
            cur.fetchone()
            cur.close()
        finally:
            release_conn(conn)
        return jsonify({"database": "neon", "engine": "postgresql", "status": "connected"})
    except Exception as exc:
        return jsonify({"database": "neon", "engine": "postgresql", "status": "error", "message": str(exc)}), 503

@app.route("/products/<category>")
def get_products(category):
    conn = get_conn()
    try:
        cur = conn.cursor()
        if category == "all":
            cur.execute("""
                SELECT id, name, price, image, category, description,
                       COALESCE(rating, 4.5) AS rating
                FROM products
            """)
        else:
            execute_query(cur, """
                SELECT id, name, price, image, category, description,
                       COALESCE(rating, 4.5) AS rating
                FROM products WHERE category=?
            """, (category,))
        rows = cur.fetchall()

        result = []
        for r in rows:
            result.append({
                "id": r[0],
                "name": r[1],
                "price": float(r[2]) if r[2] is not None else 0,
                "image": r[3],
                "category": r[4],
                "description": r[5],
                "rating": float(r[6]) if r[6] is not None else 4.5,
            })
        return jsonify(result)
    except Exception as e:
        print(f"Get products failed: {e}")
        return jsonify({"msg": "Could not load products", "error": str(e)}), 500
    finally:
        release_conn(conn)

# ---------------- MULTI-AGENT SYSTEM ----------------
def route_query(message):
    return classify_route(message)


def sales_agent(message):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT name, price, category, description, COALESCE(rating, 4.5) AS rating
            FROM products ORDER BY category, name
        """)
        products = cur.fetchall()
    finally:
        release_conn(conn)

    reply = local_sales_reply(message, products)
    print("Sales agent: database-backed reply")
    return "Sales Expert", reply


def support_agent(message):
    reply = local_support_reply(message)
    print("Support agent: policy-backed reply")
    return "Support Team", reply


def order_agent(message, user_email):
    conn = get_conn()
    try:
        cur = conn.cursor()
        if user_email:
            execute_query(
                cur,
                "SELECT id, status, total_amount, created_at, tracking_number, customer_name, shipping_address "
                "FROM orders WHERE user_email=? ORDER BY created_at DESC LIMIT 10",
                (user_email,),
            )
            orders = cur.fetchall()
        else:
            orders = []
    finally:
        release_conn(conn)

    reply = local_order_reply(message, orders, user_email)
    print("Order agent: database-backed reply")
    return "Order Assistant", reply

@app.route("/chat", methods=["POST"])
def multi_agent_chat():
    user_msg = request.json.get("message")
    if not user_msg:
        return jsonify({"msg": "No message provided"}), 400

    user_email = None
    try:
        verify_jwt_in_request(optional=True)
        user_email = get_jwt_identity()
    except Exception:
        pass
        
    print(f"Chat request received: {user_msg} | User: {user_email}")
    
    route = route_query(user_msg)
    print(f"Router decided route: {route}")
    
    if route == "SALES":
        agent_name, reply = sales_agent(user_msg)
    elif route == "ORDER":
        agent_name, reply = order_agent(user_msg, user_email)
    else:
        agent_name, reply = support_agent(user_msg)
        
    return jsonify({
        "agent": agent_name,
        "route": route,
        "reply": reply
    })

if __name__ == "__main__":
    app.run(port=5000, debug=True)
