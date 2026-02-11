from flask import Blueprint, redirect, session, url_for, render_template, request, jsonify, current_app
from backend.database.db_config import get_db_connection

order_bp = Blueprint("order_bp", __name__)

# ---------------- PLACE ORDER ----------------
@order_bp.route("/order/<int:product_id>", methods=["POST"])
def place_order(product_id):
    # Check if user is logged in
    if "user_id" not in session:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                "success": False,
                "error": "Please login to place order",
                "redirect": url_for("auth_bp.login")
            }), 401
        return redirect(url_for("auth_bp.login"))

    user_id = session["user_id"]
    user_name = session.get("user_name", "Customer")
    
    # Get quantity from form (default to 1 if not provided)
    quantity = request.form.get("quantity", 1, type=int)
    
    conn = get_db_connection()
    if conn is None:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                "success": False,
                "error": "Database connection failed"
            }), 500
        return "Database connection failed", 500

    cursor = conn.cursor(dictionary=True)

    try:
        # 1️⃣ Get product details
        cursor.execute("SELECT id, name, price FROM products WHERE id = %s", (product_id,))
        product = cursor.fetchone()

        if not product:
            cursor.close()
            conn.close()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    "success": False,
                    "error": "Product not found"
                }), 404
            return "Product not found", 404

        price = product["price"]
        total_amount = price * quantity

        # 2️⃣ Create order
        cursor.execute(
            "INSERT INTO orders (user_id, total_amount, status) VALUES (%s, %s, 'PAID')",
            (user_id, total_amount)
        )
        order_id = cursor.lastrowid

        # 3️⃣ Insert order item with quantity
        cursor.execute(
            """
            INSERT INTO order_items (order_id, product_id, quantity, price)
            VALUES (%s, %s, %s, %s)
            """,
            (order_id, product_id, quantity, price)
        )

        conn.commit()
        
        # 4️⃣ SEND REAL-TIME NOTIFICATION TO ADMINS
        try:
            from backend.app import socketio
            socketio.emit('new_order', {
                'order_id': order_id,
                'user_name': user_name,
                'product_name': product["name"],
                'quantity': quantity,
                'total_amount': float(total_amount),
                'status': 'PAID',
                'order_time': 'Just now'
            }, room='admins')
            print(f"🔔 Real-time notification sent for Order #{order_id}")
        except Exception as e:
            print(f"⚠️ SocketIO notification failed: {e}")
        
        # 5️⃣ Check if it's AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            cursor.close()
            conn.close()
            return jsonify({
                "success": True,
                "message": f"Order placed successfully! Order #{order_id}",
                "order_id": order_id,
                "product_name": product["name"],
                "quantity": quantity,
                "total": total_amount,
                "redirect": url_for("payment_bp.payment", order_id=order_id)
            })
        else:
            cursor.close()
            conn.close()
            return redirect(url_for("payment_bp.payment", order_id=order_id))
            
    except Exception as e:
        print(f"Error placing order: {e}")
        conn.rollback()
        cursor.close()
        conn.close()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                "success": False,
                "error": "Something went wrong. Please try again."
            }), 500
        return "Something went wrong", 500


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
            o.order_time,
            oi.product_id,
            oi.quantity,
            oi.price,
            p.name AS product_name,
            p.image
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        JOIN products p ON oi.product_id = p.id
        WHERE o.user_id = %s
        ORDER BY o.order_time DESC
    """, (user_id,))

    orders = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("my_orders.html", orders=orders)