# from flask import Blueprint, redirect, session, url_for, render_template, request, jsonify, current_app
# from backend.database.db_config import get_db_connection

# order_bp = Blueprint("order_bp", __name__)

# # ---------------- PLACE ORDER ----------------
# @order_bp.route("/order/<int:product_id>", methods=["POST"])
# def place_order(product_id):
#     # Check if user is logged in
#     if "user_id" not in session:
#         if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#             return jsonify({
#                 "success": False,
#                 "error": "Please login to place order",
#                 "redirect": url_for("auth_bp.login")
#             }), 401
#         return redirect(url_for("auth_bp.login"))

#     user_id = session["user_id"]
#     user_name = session.get("user_name", "Customer")
    
#     # Get quantity from form (default to 1 if not provided)
#     quantity = request.form.get("quantity", 1, type=int)
    
#     conn = get_db_connection()
#     if conn is None:
#         if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#             return jsonify({
#                 "success": False,
#                 "error": "Database connection failed"
#             }), 500
#         return "Database connection failed", 500

#     cursor = conn.cursor(dictionary=True)

#     try:
#         # 1️⃣ Get product details
#         cursor.execute("SELECT id, name, price FROM products WHERE id = %s", (product_id,))
#         product = cursor.fetchone()

#         if not product:
#             cursor.close()
#             conn.close()
#             if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#                 return jsonify({
#                     "success": False,
#                     "error": "Product not found"
#                 }), 404
#             return "Product not found", 404

#         price = product["price"]
#         total_amount = price * quantity

#         # 2️⃣ Create order with 'pending' status
#         cursor.execute(
#             "INSERT INTO orders (user_id, total_amount, status) VALUES (%s, %s, 'pending')",
#             (user_id, total_amount)
#         )
#         order_id = cursor.lastrowid

#         # 3️⃣ Insert order item with quantity
#         cursor.execute(
#             """
#             INSERT INTO order_items (order_id, product_id, quantity, price)
#             VALUES (%s, %s, %s, %s)
#             """,
#             (order_id, product_id, quantity, price)
#         )

#         conn.commit()
        
#         # 4️⃣ SEND REAL-TIME NOTIFICATION TO ADMINS
#         try:
#             from backend.app import socketio
#             socketio.emit('new_order', {
#                 'order_id': order_id,
#                 'user_name': user_name,
#                 'product_name': product["name"],
#                 'quantity': quantity,
#                 'total_amount': float(total_amount),
#                 'status': 'pending',
#                 'order_time': 'Just now'
#             }, room='admins')
#             print(f"🔔 Real-time notification sent for Order #{order_id}")
#         except Exception as e:
#             print(f"⚠️ SocketIO notification failed: {e}")
        
#         # 5️⃣ Check if it's AJAX request
#         if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#             cursor.close()
#             conn.close()
#             return jsonify({
#                 "success": True,
#                 "message": f"Order placed successfully! Order #{order_id}",
#                 "order_id": order_id,
#                 "product_name": product["name"],
#                 "quantity": quantity,
#                 "total": total_amount,
#                 "status": "pending",
#                 "redirect": url_for("payment_bp.payment", order_id=order_id)
#             })
#         else:
#             cursor.close()
#             conn.close()
#             return redirect(url_for("payment_bp.payment", order_id=order_id))
            
#     except Exception as e:
#         print(f"Error placing order: {e}")
#         conn.rollback()
#         cursor.close()
#         conn.close()
#         if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#             return jsonify({
#                 "success": False,
#                 "error": "Something went wrong. Please try again."
#             }), 500
#         return "Something went wrong", 500


# # ---------------- MY ORDERS (USER) ----------------
# @order_bp.route("/my-orders")
# def my_orders():
#     if "user_id" not in session:
#         return redirect(url_for("auth_bp.login"))

#     user_id = session["user_id"]

#     conn = get_db_connection()
#     if conn is None:
#         return "Database connection failed", 500

#     cursor = conn.cursor(dictionary=True)

#     # FIXED: Properly get all order details with order_id
#     cursor.execute("""
#         SELECT 
#             o.id AS order_id,
#             o.total_amount,
#             o.status,
#             o.order_time,
#             oi.product_id,
#             oi.quantity,
#             oi.price,
#             p.name AS product_name,
#             p.image
#         FROM orders o
#         JOIN order_items oi ON o.id = oi.order_id
#         JOIN products p ON oi.product_id = p.id
#         WHERE o.user_id = %s
#         ORDER BY o.order_time DESC
#     """, (user_id,))

#     orders = cursor.fetchall()
    
#     # Format orders for display
#     for order in orders:
#         # Ensure order_id is properly formatted
#         order['display_id'] = f"#{order['order_id']}"
        
#         # Format status for display
#         if order['status'] == 'pending':
#             order['status_display'] = 'PENDING'
#             order['status_color'] = '#f59e0b'  # Orange
#             order['action_text'] = 'Processing'
#             order['action_color'] = '#f59e0b'
#         elif order['status'] == 'accepted':
#             order['status_display'] = 'ACCEPTED'
#             order['status_color'] = '#3b82f6'  # Blue
#             order['action_text'] = 'Preparing'
#             order['action_color'] = '#3b82f6'
#         elif order['status'] == 'completed':
#             order['status_display'] = 'COMPLETED'
#             order['status_color'] = '#10b981'  # Green
#             order['action_text'] = 'Delivered'
#             order['action_color'] = '#10b981'
#         elif order['status'] == 'rejected':
#             order['status_display'] = 'REJECTED'
#             order['status_color'] = '#ef4444'  # Red
#             order['action_text'] = 'Cancelled'
#             order['action_color'] = '#ef4444'
#         else:
#             order['status_display'] = order['status'].upper()
#             order['status_color'] = '#6b7280'  # Gray
#             order['action_text'] = 'Processing'
#             order['action_color'] = '#6b7280'

#     cursor.close()
#     conn.close()

#     return render_template("my_orders.html", orders=orders)



from flask import Blueprint, redirect, session, url_for, render_template, request, jsonify
from backend.database.db_config import get_db_connection

order_bp = Blueprint("order_bp", __name__)

# ---------------- PLACE ORDER ----------------
@order_bp.route("/order/<int:product_id>", methods=["POST"])
def place_order(product_id):
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
    quantity = request.form.get("quantity", 1, type=int)

    conn = get_db_connection()
    if conn is None:
        return "Database connection failed", 500

    cursor = conn.cursor()   # ✅ FIXED

    try:
        # 1️⃣ Get product
        cursor.execute(
            "SELECT id, name, price FROM products WHERE id = %s",
            (product_id,)
        )
        product = cursor.fetchone()

        if not product:
            cursor.close()
            conn.close()
            return "Product not found", 404

        price = product["price"]
        total_amount = price * quantity

        # 2️⃣ Insert order (PostgreSQL FIX using RETURNING id)
        cursor.execute(
            """
            INSERT INTO orders (user_id, total_amount, status)
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (user_id, total_amount, 'PENDING')
        )

        order_id = cursor.fetchone()["id"]

        # 3️⃣ Insert order item
        cursor.execute(
            """
            INSERT INTO order_items (order_id, product_id, quantity, price)
            VALUES (%s, %s, %s, %s)
            """,
            (order_id, product_id, quantity, price)
        )

        conn.commit()

        # 4️⃣ Real-time notification
        try:
            from backend.app import socketio
            socketio.emit('new_order', {
                'order_id': order_id,
                'user_name': user_name,
                'product_name': product["name"],
                'quantity': quantity,
                'total_amount': float(total_amount),
                'status': 'PENDING',
                'order_time': 'Just now'
            }, room='admins')
        except Exception as e:
            print("SocketIO error:", e)

        cursor.close()
        conn.close()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                "success": True,
                "message": f"Order placed successfully! Order #{order_id}",
                "order_id": order_id,
                "redirect": url_for("payment_bp.payment", order_id=order_id)
            })

        return redirect(url_for("payment_bp.payment", order_id=order_id))

    except Exception as e:
        print("Order error:", e)
        conn.rollback()
        cursor.close()
        conn.close()
        return "Something went wrong", 500


# ---------------- MY ORDERS ----------------
@order_bp.route("/my-orders")
def my_orders():
    if "user_id" not in session:
        return redirect(url_for("auth_bp.login"))

    user_id = session["user_id"]

    conn = get_db_connection()
    if conn is None:
        return "Database connection failed", 500

    cursor = conn.cursor()   # ✅ FIXED

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

    # Format status
    for order in orders:
        order['display_id'] = f"#{order['order_id']}"

        if order['status'] == 'PENDING':
            order['status_color'] = '#f59e0b'
        elif order['status'] == 'ACCEPTED':
            order['status_color'] = '#3b82f6'
        elif order['status'] == 'COMPLETED':
            order['status_color'] = '#10b981'
        elif order['status'] == 'REJECTED':
            order['status_color'] = '#ef4444'
        else:
            order['status_color'] = '#6b7280'

    cursor.close()
    conn.close()

    return render_template("my_orders.html", orders=orders)