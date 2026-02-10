from flask import Flask, render_template
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

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(menu_bp)
app.register_blueprint(order_bp)
app.register_blueprint(payment_bp)

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
