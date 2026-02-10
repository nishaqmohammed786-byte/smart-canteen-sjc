from flask import Blueprint, redirect, session, url_for, render_template
from backend.database.db_config import get_db_connection

order_bp = Blueprint("order_bp", __name__)

# ---------------- PLACE ORDER ----------------
@order_bp.route("/order/<int:product_id>", methods=["POST"])
def place_order(product_id):
    if "user_id" not in session:
        return redirect(url_for("auth_bp.login"))

    user_id = session["user_id"]

    conn = get_db_connection()
    if conn is None:
        return "Database connection failed", 500

    cursor = conn.cursor(dictionary=True)

    # 1️⃣ Get product price
    cursor.execute("SELECT price FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()

    if not product:
        cursor.close()
        conn.close()
        return "Product not found", 404

    price = product["price"]

    # 2️⃣ Create order
    cursor.execute(
        "INSERT INTO orders (user_id, total_amount, status) VALUES (%s, %s, 'PENDING')",
        (user_id, price)
    )
    order_id = cursor.lastrowid

    # 3️⃣ Insert order item
    cursor.execute(
        """
        INSERT INTO order_items (order_id, product_id, quantity, price)
        VALUES (%s, %s, %s, %s)
        """,
        (order_id, product_id, 1, price)
    )

    conn.commit()
    cursor.close()
    conn.close()

    # 4️⃣ Redirect to fake Paytm
    return redirect(url_for("payment_bp.payment", order_id=order_id))


# ---------------- MY ORDERS (USER) ----------------
@order_bp.route("/my-orders")
def my_orders():
    if "user_id" not in session:
        return redirect(url_for("auth_bp.login"))

    user_id = session["user_id"]

    conn = get_db_connection()
    if conn is None:
        return "Database connection failed", 500

    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            o.id AS order_id,
            o.total_amount,
            o.status,
            o.order_time
        FROM orders o
        WHERE o.user_id = %s
        ORDER BY o.order_time DESC
    """, (user_id,))

    orders = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("user_orders.html", orders=orders)
