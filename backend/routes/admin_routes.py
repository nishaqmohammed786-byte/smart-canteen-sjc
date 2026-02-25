from flask import Blueprint, render_template, redirect, session, url_for, request, jsonify
from backend.database.db_config import get_db_connection
from datetime import datetime

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

    # Get pending orders count (pending = waiting to be accepted)
    cursor.execute("""
        SELECT COUNT(*) AS pending_count
        FROM orders
        WHERE status = 'pending'
    """)
    pending_count = cursor.fetchone()["pending_count"]
    
    # Get total orders count
    cursor.execute("""
        SELECT COUNT(*) AS total_count
        FROM orders
    """)
    total_count = cursor.fetchone()["total_count"]
    
    # Get active menu items count
    cursor.execute("""
        SELECT COUNT(*) AS menu_count
        FROM products
    """)
    menu_count = cursor.fetchone()["menu_count"]
    
    # Get TODAY'S revenue from completed orders
    cursor.execute("""
        SELECT COALESCE(SUM(total_amount), 0) AS revenue
        FROM orders
        WHERE DATE(order_time) = CURDATE() 
        AND status = 'completed'
    """)
    revenue = cursor.fetchone()["revenue"]
    
    # Get recent orders for dashboard preview
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
        LIMIT 5
    """)
    recent_orders = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "admin_dashboard.html",
        pending_count=pending_count,
        total_orders=total_count,
        menu_count=menu_count,
        revenue=revenue,
        recent_orders=recent_orders,
        datetime=datetime
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

    # Get all orders with items
    cursor.execute("""
        SELECT
            o.id AS order_id,
            u.name AS user_name,
            o.total_amount,
            o.status,
            o.order_time,
            GROUP_CONCAT(CONCAT(p.name, ' (', oi.quantity, ')') SEPARATOR ', ') AS items,
            COUNT(oi.id) AS items_count
        FROM orders o
        JOIN users u ON o.user_id = u.id
        LEFT JOIN order_items oi ON o.id = oi.order_id
        LEFT JOIN products p ON oi.product_id = p.id
        GROUP BY o.id
        ORDER BY o.order_time DESC
    """)

    orders = cursor.fetchall()
    
    # Convert items to string for template
    for order in orders:
        if order['items'] is None:
            order['items'] = ''
        else:
            order['items'] = str(order['items'])
        
        # Create display field
        order['items_display'] = order['items']
        
        if order['items_count'] is None:
            order['items_count'] = 0
        else:
            order['items_count'] = int(order['items_count'])

    cursor.close()
    conn.close()

    return render_template("admin_orders.html", orders=orders)


# ---------------- ACCEPT ORDER ----------------
@admin_bp.route("/accept/<int:order_id>")
def accept_order(order_id):
    if session.get("role") != "admin":
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"success": False, "error": "Unauthorized"}), 401
        return redirect(url_for("auth_bp.login"))

    conn = get_db_connection()
    if conn is None:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"success": False, "error": "Database connection failed"}), 500
        return "Database connection failed", 500

    cursor = conn.cursor()
    
    try:
        # Update order status to accepted
        cursor.execute(
            "UPDATE orders SET status = 'accepted' WHERE id = %s",
            (order_id,)
        )
        conn.commit()
        
        # Send real-time update
        try:
            from backend.app import socketio
            socketio.emit('order_status_updated', {
                'order_id': order_id,
                'status': 'accepted',
                'message': f'Order #{order_id} has been accepted'
            }, room='admins')
        except:
            pass
        
        cursor.close()
        conn.close()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                "success": True, 
                "status": "accepted",
                "order_id": order_id,
                "message": f"Order #{order_id} accepted successfully"
            })
        
        return redirect(url_for("admin_bp.orders"))
        
    except Exception as e:
        print(f"Error accepting order: {e}")
        conn.rollback()
        cursor.close()
        conn.close()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"success": False, "error": "Failed to accept order"}), 500
        return "Failed to accept order", 500


# ---------------- REJECT ORDER ----------------
@admin_bp.route("/reject/<int:order_id>")
def reject_order(order_id):
    if session.get("role") != "admin":
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"success": False, "error": "Unauthorized"}), 401
        return redirect(url_for("auth_bp.login"))

    conn = get_db_connection()
    if conn is None:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"success": False, "error": "Database connection failed"}), 500
        return "Database connection failed", 500

    cursor = conn.cursor()
    
    try:
        # Update order status to rejected
        cursor.execute(
            "UPDATE orders SET status = 'rejected' WHERE id = %s",
            (order_id,)
        )
        conn.commit()
        
        # Send real-time update
        try:
            from backend.app import socketio
            socketio.emit('order_status_updated', {
                'order_id': order_id,
                'status': 'rejected',
                'message': f'Order #{order_id} has been rejected'
            }, room='admins')
        except:
            pass
        
        cursor.close()
        conn.close()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                "success": True, 
                "status": "rejected",
                "order_id": order_id,
                "message": f"Order #{order_id} rejected successfully"
            })
        
        return redirect(url_for("admin_bp.orders"))
        
    except Exception as e:
        print(f"Error rejecting order: {e}")
        conn.rollback()
        cursor.close()
        conn.close()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"success": False, "error": "Failed to reject order"}), 500
        return "Failed to reject order", 500


# ---------------- COMPLETE ORDER ----------------
@admin_bp.route("/complete/<int:order_id>")
def complete_order(order_id):
    if session.get("role") != "admin":
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"success": False, "error": "Unauthorized"}), 401
        return redirect(url_for("auth_bp.login"))

    conn = get_db_connection()
    if conn is None:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"success": False, "error": "Database connection failed"}), 500
        return "Database connection failed", 500

    cursor = conn.cursor()
    
    try:
        # Get order amount before updating
        cursor.execute("SELECT total_amount FROM orders WHERE id = %s", (order_id,))
        order_result = cursor.fetchone()
        total_amount = order_result[0] if order_result else 0
        
        # Update order status to completed
        cursor.execute(
            "UPDATE orders SET status = 'completed' WHERE id = %s",
            (order_id,)
        )
        conn.commit()
        
        # Send real-time update
        try:
            from backend.app import socketio
            socketio.emit('order_status_updated', {
                'order_id': order_id,
                'status': 'completed',
                'message': f'Order #{order_id} has been completed',
                'amount': total_amount
            }, room='admins')
            
            # Also emit revenue update
            socketio.emit('revenue_updated', {
                'amount': total_amount,
                'message': f'₹{total_amount} added to today\'s revenue'
            }, room='admins')
        except:
            pass
        
        cursor.close()
        conn.close()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                "success": True, 
                "status": "completed",
                "order_id": order_id,
                "amount": total_amount,
                "message": f"Order #{order_id} completed successfully! ₹{total_amount} added to revenue"
            })
        
        return redirect(url_for("admin_bp.orders"))
        
    except Exception as e:
        print(f"Error completing order: {e}")
        conn.rollback()
        cursor.close()
        conn.close()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"success": False, "error": "Failed to complete order"}), 500
        return "Failed to complete order", 500


# ---------------- GET ORDER DETAILS (API) ----------------
@admin_bp.route("/order/<int:order_id>")
def get_order_details(order_id):
    if session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 401
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT
            o.id AS order_id,
            u.name AS user_name,
            u.email AS user_email,
            o.total_amount,
            o.status,
            o.order_time,
            GROUP_CONCAT(
                CONCAT(p.name, ' (Qty: ', oi.quantity, ', ₹', oi.price, ')')
                SEPARATOR '\n'
            ) AS items_list
        FROM orders o
        JOIN users u ON o.user_id = u.id
        LEFT JOIN order_items oi ON o.id = oi.order_id
        LEFT JOIN products p ON oi.product_id = p.id
        WHERE o.id = %s
        GROUP BY o.id
    """, (order_id,))
    
    order = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if order:
        if order['items_list'] is None:
            order['items_list'] = ''
        else:
            order['items_list'] = str(order['items_list'])
        
        return jsonify({"success": True, "order": order})
    else:
        return jsonify({"success": False, "error": "Order not found"}), 404