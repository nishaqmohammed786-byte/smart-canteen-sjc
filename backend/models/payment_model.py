from backend.database.db_config import get_db_connection

class Payment:
    @staticmethod
    def create(order_id, amount, method, status="pending"):
        """
        Create a payment record
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO payments (order_id, amount, method, status)
            VALUES (%s, %s, %s, %s)
            """,
            (order_id, amount, method, status)
        )
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def get_by_order(order_id):
        """
        Get payment details by order ID
        """
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM payments WHERE order_id = %s",
            (order_id,)
        )
        payment = cursor.fetchone()
        cursor.close()
        conn.close()
        return payment

    @staticmethod
    def update_status(payment_id, status):
        """
        Update payment status
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE payments SET status=%s WHERE id=%s",
            (status, payment_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
