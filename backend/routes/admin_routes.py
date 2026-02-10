from flask import Blueprint, render_template, redirect, session, url_for
from backend.database.db_config import get_db_connection

admin_bp = Blueprint(
    "admin_bp",
    __name__,
    url_prefix="/admin",
    template_folder="../../frontend/templates"
)

# ---------------- ADMIN DASHBOARD ----------------
@admin_bp.route("/dashboard")
def dashboard():
    if session.get("role") != "admin":
        return redirect(url_for("auth_bp.login"))

    conn = get_db_connection()
    if conn is None:
        return "Database connection failed", 500

    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT COUNT(*) AS pending_count
        FROM orders
        WHERE status = 'PAID'
    """)
    pending_count = cursor.fetchone()["pending_count"]

    cursor.close()
    conn.close()

    return render_template(
        "admin_dashboard.html",
        pending_count=pending_count
    )


# ---------------- VIEW ALL ORDERS ----------------
@admin_bp.route("/orders")
def orders():
    if session.get("role") != "admin":
        return redirect(url_for("auth_bp.login"))

    conn = get_db_connection()
    if conn is None:
        return "Database connection failed", 500

    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            o.id AS order_id,
            u.name AS user_name,
            o.total_amount,
            o.status,
            o.order_time
        FROM orders o
        JOIN users u ON o.user_id = u.id
        ORDER BY o.order_time DESC
    """)

    orders = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("admin_orders.html", orders=orders)


# ---------------- ACCEPT ORDER ----------------
@admin_bp.route("/accept/<int:order_id>")
def accept_order(order_id):
    if session.get("role") != "admin":
        return redirect(url_for("auth_bp.login"))

    conn = get_db_connection()
    if conn is None:
        return "Database connection failed", 500

    cursor = conn.cursor()
    cursor.execute(
        "UPDATE orders SET status = 'ACCEPTED' WHERE id = %s",
        (order_id,)
    )
    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for("admin_bp.orders"))


# ---------------- REJECT ORDER ----------------
@admin_bp.route("/reject/<int:order_id>")
def reject_order(order_id):
    if session.get("role") != "admin":
        return redirect(url_for("auth_bp.login"))

    conn = get_db_connection()
    if conn is None:
        return "Database connection failed", 500

    cursor = conn.cursor()
    cursor.execute(
        "UPDATE orders SET status = 'REJECTED' WHERE id = %s",
        (order_id,)
    )
    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for("admin_bp.orders"))
