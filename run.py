from backend.app import app, socketio
from backend.database.db_config import get_local_ip
import socket

if __name__ == "__main__":
    local_ip = get_local_ip()
    
    print("\n" + "="*50)
    print("🚀 SJC CANTEEN SERVER STARTING...")
    print("="*50)
    print(f"📍 Local URL: http://127.0.0.1:5000")
    print(f"📍 Network URL: http://{local_ip}:5000")
    print(f"📱 Mobile URL: http://{local_ip}:5000 (same WiFi)")
    print("="*50 + "\n")
    
    # Run on all interfaces (0.0.0.0) so both localhost and IP work
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)