# import eventlet
# eventlet.monkey_patch()

# from backend.app import app, socketio
# import os

# port = int(os.environ.get("PORT", 5000))

# if __name__ == "__main__":
#     print("\n" + "="*50)
#     print("🚀 SJC CANTEEN SERVER STARTING...")
#     print("="*50)
#     print(f"📍 Running on PORT: {port}")
#     print("="*50 + "\n")

#     socketio.run(app, host="0.0.0.0", port=port)



import eventlet
eventlet.monkey_patch()

from backend.app import app, socketio
import os

port = int(os.environ.get("PORT", 5000))

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=port)