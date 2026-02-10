from backend.database.db_config import get_db_connection



class MenuItem:
    @staticmethod
    def all_items():
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM menu")
        items = cursor.fetchall()
        cursor.close()
        conn.close()
        return items

    @staticmethod
    def create(item_name, price):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO menu (item_name, price) VALUES (%s, %s)",
            (item_name, price)
        )
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def update(item_id, item_name, price, available):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE menu SET item_name=%s, price=%s, available=%s WHERE id=%s",
            (item_name, price, available, item_id)
        )
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def delete(item_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM menu WHERE id=%s", (item_id,))
        conn.commit()
        cursor.close()
        conn.close()
