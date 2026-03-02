import mysql.connector
from mysql.connector import Error
import socket

def get_db_connection():
    try:
        # Try localhost first (fastest)
        try:
            connection = mysql.connector.connect(
                host='127.0.0.1',
                user='root',
                password='',
                database='smart_canteen',
                port=3306,
                connection_timeout=5
            )
            print("✅ Connected to MySQL via localhost")
            return connection
        except Error:
            # If localhost fails, try with IP address
            print("⚠️ Localhost connection failed, trying IP address...")
            
            # Get your local IP address
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            connection = mysql.connector.connect(
                host=local_ip,  # Your actual IP (e.g., 10.14.128.176)
                user='root',
                password='',
                database='smart_canteen',
                port=3306
            )
            print(f"✅ Connected to MySQL via IP: {local_ip}")
            return connection
            
    except Error as e:
        print(f"❌ Error connecting to MySQL: {e}")
        return None

# Optional: Function to get your local IP
def get_local_ip():
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return local_ip
    except:
        return "127.0.0.1"