from flask import Blueprint, render_template, session, redirect, url_for
from backend.database.db_config import get_db_connection

user_bp = Blueprint("user_bp", __name__)

@user_bp.route("/my-orders")
def my_orders():
    if "user_id" not in session:
        return redirect(url_for("auth_bp.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT orders.id, products.name, products.image, orders.status, orders.order_time
        FROM orders
        JOIN products ON orders.product_id = products.id
        WHERE orders.user_id = %s
        ORDER BY orders.id DESC
    """, (session["user_id"],))

    orders = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("user_orders.html", orders=orders)
