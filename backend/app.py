# from flask import Flask, render_template, request, session
# from flask_socketio import SocketIO, emit, join_room, leave_room
# import os

# from backend.routes.auth_routes import auth_bp
# from backend.routes.admin_routes import admin_bp
# from backend.routes.menu_routes import menu_bp
# from backend.routes.order_routes import order_bp
# from backend.routes.payment_routes import payment_bp

# app = Flask(
#     __name__,
#     template_folder="../frontend/templates",
#     static_folder="../frontend/static"
# )

# app.secret_key = "super-secret-key"
# app.config['SECRET_KEY'] = 'super-secret-key'

# # Initialize SocketIO
# socketio = SocketIO(app, cors_allowed_origins="*")

# # Register Blueprints
# app.register_blueprint(auth_bp)
# app.register_blueprint(admin_bp)
# app.register_blueprint(menu_bp)
# app.register_blueprint(order_bp)
# app.register_blueprint(payment_bp)

# # Make socketio available in other files
# def get_socketio():
#     return socketio

# # ---------- SOCKETIO EVENTS ----------
# @socketio.on('connect')
# def handle_connect():
#     print(f'Client connected: {request.sid}')
    
#     # Check if user is admin and join admin room
#     from flask import session
#     if session.get('role') == 'admin':
#         join_room('admins')
#         print(f'Admin joined room: {session.get("user_name")}')

# @socketio.on('disconnect')
# def handle_disconnect():
#     print(f'Client disconnected: {request.sid}')
#     if session.get('role') == 'admin':
#         leave_room('admins')

# @socketio.on('join_admin_room')
# def handle_join_admin_room():
#     join_room('admins')
#     emit('admin_joined', {'message': 'Admin connected'}, room='admins')

# # ---------- ROUTES ----------
# @app.route("/")
# def home():
#     return render_template("index.html")

# # Export socketio for use in other routes
# app.socketio = socketio

# if __name__ == "__main__":
#     socketio.run(app, debug=True, allow_unsafe_werkzeug=True)




from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, emit, join_room, leave_room
import os

from backend.routes.auth_routes import auth_bp
from backend.routes.admin_routes import admin_bp
from backend.routes.menu_routes import menu_bp
from backend.routes.order_routes import order_bp
from backend.routes.payment_routes import payment_bp

# ✅ Import DB connection
from backend.database.db_config import get_db_connection


app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)

app.secret_key = "super-secret-key"
app.config['SECRET_KEY'] = 'super-secret-key'

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(menu_bp)
app.register_blueprint(order_bp)
app.register_blueprint(payment_bp)

# Make socketio available in other files
def get_socketio():
    return socketio


# ---------- SOCKETIO EVENTS ----------
@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')
    
    if session.get('role') == 'admin':
        join_room('admins')
        print(f'Admin joined room: {session.get("user_name")}')


@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')
    if session.get('role') == 'admin':
        leave_room('admins')


@socketio.on('join_admin_room')
def handle_join_admin_room():
    join_room('admins')
    emit('admin_joined', {'message': 'Admin connected'}, room='admins')


# ---------- ROUTES ----------
@app.route("/")
def home():
    return render_template("index.html")


# 🔥 TEMPORARY ROUTE TO CREATE TABLES
@app.route("/create-tables")
def create_tables():
    conn = get_db_connection()
    if not conn:
        return "❌ Database connection failed!"

    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        role VARCHAR(10) DEFAULT 'user'
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        price DECIMAL(10,2) NOT NULL,
        image VARCHAR(255)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        total_amount DECIMAL(10,2) NOT NULL,
        status VARCHAR(20) DEFAULT 'PENDING',
        order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        id SERIAL PRIMARY KEY,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER DEFAULT 1,
        price DECIMAL(10,2) NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id SERIAL PRIMARY KEY,
        order_id INTEGER NOT NULL,
        payment_method VARCHAR(50) DEFAULT 'PAYTM',
        status VARCHAR(20) DEFAULT 'SUCCESS',
        payment_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
    );
    """)

    cur.execute("""
    INSERT INTO users (name, email, password, role)
    VALUES ('Admin', 'admin@gmail.com', 'admin123', 'admin')
    ON CONFLICT (email) DO NOTHING;
    """)

    conn.commit()
    cur.close()
    conn.close()

    return "✅ Tables Created Successfully!"


# Export socketio
app.socketio = socketio


if __name__ == "__main__":
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)