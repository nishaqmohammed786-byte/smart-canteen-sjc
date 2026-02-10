from backend.database.db_config import get_db_connection

def get_all_menu():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM menu")
    result = cursor.fetchall()
    conn.close()
    return result

def add_menu_item(name, price):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO menu (name, price) VALUES (%s, %s)", (name, price))
    conn.commit()
    conn.close()

def delete_menu_item(menu_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM menu WHERE id=%s", (menu_id,))
    conn.commit()
    conn.close()
