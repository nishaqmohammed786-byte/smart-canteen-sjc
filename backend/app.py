from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, emit, join_room, leave_room
import os

from backend.routes.auth_routes import auth_bp
from backend.routes.admin_routes import admin_bp
from backend.routes.menu_routes import menu_bp
from backend.routes.order_routes import order_bp
from backend.routes.payment_routes import payment_bp

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
    
    # Check if user is admin and join admin room
    from flask import session
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

# Export socketio for use in other routes
app.socketio = socketio

if __name__ == "__main__":
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)