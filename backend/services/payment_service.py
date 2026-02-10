# backend/services/payment_service.py
from backend.database.db_config import get_db_connection

def record_payment(order_id, amount, method):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO payments (order_id, amount, method) VALUES (%s, %s, %s)",
                   (order_id, amount, method))
    conn.commit()
    conn.close()
