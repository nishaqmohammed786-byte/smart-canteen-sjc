from backend.database.db_config import get_db_connection



class Order:
    @staticmethod
    def create(user_id, item_id, quantity=1):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO orders (user_id, item_id, quantity, status) VALUES (%s,%s,%s,%s)",
            (user_id, item_id, quantity, 'pending')
        )
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def get_by_user(user_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT o.id, o.quantity, o.status, o.created_at,
                   m.item_name, m.price
            FROM orders o
            JOIN menu m ON o.item_id = m.id
            WHERE o.user_id = %s
        """, (user_id,))
        orders = cursor.fetchall()
        cursor.close()
        conn.close()
        return orders

    @staticmethod
    def update_status(order_id, status):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE orders SET status=%s WHERE id=%s",
            (status, order_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
