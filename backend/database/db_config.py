import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",          # MUST be string
            database="smart_canteen",
            port=3306
        )
        return conn
    except Error as e:
        print("❌ Database connection error:", e)
        return None
