from flask import Blueprint, render_template, redirect, session, request, url_for
from backend.database.db_config import get_db_connection

payment_bp = Blueprint("payment_bp", __name__)

# ---------------- FAKE PAYTM PAYMENT ----------------
@payment_bp.route("/pay/<int:order_id>", methods=["GET", "POST"])
def payment(order_id):
    if "user_id" not in session:
        return redirect(url_for("auth_bp.login"))

    user_id = session["user_id"]

    conn = get_db_connection()
    if conn is None:
        return "Database connection failed", 500

    cursor = conn.cursor(dictionary=True)

    # 1️⃣ Fetch order
    cursor.execute("""
        SELECT id, total_amount, status
        FROM orders
        WHERE id = %s AND user_id = %s
    """, (order_id, user_id))

    order = cursor.fetchone()

    if not order:
        cursor.close()
        conn.close()
        return "Order not found", 404

    # 2️⃣ Handle payment confirmation
    if request.method == "POST":
        # Insert payment record (fake Paytm)
        cursor.execute("""
            INSERT INTO payments (order_id, payment_method, status)
            VALUES (%s, 'PAYTM', 'SUCCESS')
        """, (order_id,))

        # Update order status to PAID
        cursor.execute("""
            UPDATE orders SET status = 'PAID' WHERE id = %s
        """, (order_id,))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for("payment_bp.payment_success", order_id=order_id))

    cursor.close()
    conn.close()

    return render_template("payment.html", order=order)


# ---------------- PAYMENT SUCCESS ----------------
@payment_bp.route("/payment-success/<int:order_id>")
def payment_success(order_id):
    if "user_id" not in session:
        return redirect(url_for("auth_bp.login"))

    return render_template("payment_success.html", order_id=order_id)
