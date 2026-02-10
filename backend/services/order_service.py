# backend/services/order_service.py
from backend.database.db_config import get_db_connection

def place_order(user_id, menu_id, quantity):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders (user_id, menu_id, quantity) VALUES (%s, %s, %s)",
                   (user_id, menu_id, quantity))
    conn.commit()
    conn.close()

def get_user_orders(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT o.id, m.name, m.price, o.quantity 
        FROM orders o JOIN menu m ON o.menu_id = m.id
        WHERE o.user_id=%s
    """, (user_id,))
    result = cursor.fetchall()
    conn.close()
    return result

def get_all_orders():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT o.id, u.email, m.name, o.quantity, m.price 
        FROM orders o
        JOIN menu m ON o.menu_id = m.id
        JOIN users u ON o.user_id = u.id
    """)
    result = cursor.fetchall()
    conn.close()
    return result
