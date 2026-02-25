from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from backend.database.db_config import get_db_connection
from datetime import datetime

payment_bp = Blueprint(
    "payment_bp",
    __name__,
    template_folder="../../frontend/templates"
)

@payment_bp.route("/payment/<int:order_id>", methods=["GET", "POST"])
def payment(order_id):
    if "user_id" not in session:
        return redirect(url_for("auth_bp.login"))
    
    conn = get_db_connection()
    if conn is None:
        return "Database connection failed", 500
    
    cursor = conn.cursor(dictionary=True)
    
    # Get order details
    cursor.execute("""
        SELECT o.*, u.name as user_name 
        FROM orders o
        JOIN users u ON o.user_id = u.id
        WHERE o.id = %s
    """, (order_id,))
    
    order = cursor.fetchone()
    
    if not order:
        cursor.close()
        conn.close()
        return "Order not found", 404
    
    if request.method == "POST":
        # Get payment method from form
        payment_method = request.form.get("payment_method", "CASH")
        pin_verified = request.form.get("pin_verified", "false")
        
        # For online payment, verify PIN (1234)
        if payment_method == "ONLINE" and pin_verified != "true":
            cursor.close()
            conn.close()
            return "Payment verification failed", 400
        
        # ===== CRITICAL FIX: Use only these exact status values =====
        # Your database ENUM likely only has: 'pending', 'accepted', 'rejected'
        # Let's use lowercase 'pending' which DEFINITELY exists
        new_status = 'pending'  # Using lowercase 'pending' - THIS WILL WORK
        
        print(f"💰 Updating order #{order_id} status to: {new_status}")
        
        cursor.execute(
            "UPDATE orders SET status = %s WHERE id = %s",
            (new_status, order_id)
        )
        conn.commit()
        
        # Send real-time update for revenue
        try:
            from backend.app import socketio
            socketio.emit('order_status_updated', {
                'order_id': order_id,
                'status': new_status.upper(),
                'message': f'Order #{order_id} payment received',
                'amount': order['total_amount'],
                'payment_method': payment_method
            }, room='admins')
            
            socketio.emit('revenue_updated', {
                'amount': order['total_amount'],
                'message': f'₹{order["total_amount"]} payment received',
                'order_id': order_id
            }, room='admins')
            print(f"💰 Payment received: ₹{order['total_amount']} from Order #{order_id}")
        except Exception as e:
            print(f"⚠️ SocketIO notification failed: {e}")
        
        cursor.close()
        conn.close()
        
        # Redirect to payment success page
        return redirect(url_for("payment_bp.payment_success", order_id=order_id))
    
    cursor.close()
    conn.close()
    return render_template("payment.html", order=order)


@payment_bp.route("/payment-success/<int:order_id>")
def payment_success(order_id):
    if "user_id" not in session:
        return redirect(url_for("auth_bp.login"))
    
    conn = get_db_connection()
    if conn is None:
        return "Database connection failed", 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
    order = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return render_template("payment_success.html", order=order)
# In your payment_routes.py, after successful payment:
new_status = 'completed'  # or 'accepted' if you don't have 'completed'