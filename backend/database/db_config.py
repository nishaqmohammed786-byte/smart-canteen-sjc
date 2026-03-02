# import mysql.connector
# from mysql.connector import Error
# import socket

# def get_db_connection():
#     try:
#         # Try localhost first (fastest)
#         try:
#             connection = mysql.connector.connect(
#                 host='127.0.0.1',
#                 user='root',
#                 password='1234',
#                 database='smart_canteen',
#                 port=3306,
#                 connection_timeout=5
#             )
#             print("✅ Connected to MySQL via localhost")
#             return connection
#         except Error:
#             # If localhost fails, try with IP address
#             print("⚠️ Localhost connection failed, trying IP address...")
            
#             # Get your local IP address
#             hostname = socket.gethostname()
#             local_ip = socket.gethostbyname(hostname)
            
#             connection = mysql.connector.connect(
#                 host=local_ip,  # Your actual IP (e.g., 10.14.128.176)
#                 user='root',
#                 password='1234',
#                 database='smart_canteen',
#                 port=3306
#             )
#             print(f"✅ Connected to MySQL via IP: {local_ip}")
#             return connection
            
#     except Error as e:
#         print(f"❌ Error connecting to MySQL: {e}")
#         return None

# # Optional: Function to get your local IP
# def get_local_ip():
#     try:
#         hostname = socket.gethostname()
#         local_ip = socket.gethostbyname(hostname)
#         return local_ip
#     except:
#         return "127.0.0.1"




import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    try:
        # First try environment variable (Render)
        database_url = os.environ.get("DATABASE_URL")

        # If not found, use your Render DB directly (for local testing)
        if not database_url:
            print("⚠️ Using fallback database URL")
            database_url = "postgresql://smart_canteen_user:eAnYT1qQ5yS8kUQ12LsUl15zC8aazzxW@dpg-d6jau8p5pdvs73eoqrh0-a.oregon-postgres.render.com/smart_canteen"

        conn = psycopg2.connect(
            database_url,
            cursor_factory=RealDictCursor,
            connect_timeout=5
        )

        print("✅ Connected to PostgreSQL")
        return conn

    except Exception as e:
        print("❌ DB Error:", e)
        return None