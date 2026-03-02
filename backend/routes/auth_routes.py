# from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
# from backend.database.db_config import get_db_connection
# import random
# import string

# auth_bp = Blueprint(
#     "auth_bp",
#     __name__,
#     template_folder="../../frontend/templates"
# )

# # Admin credentials (hardcoded for demo)
# ADMIN_EMAIL = "admin@sjctrichy.edu"
# ADMIN_PASSWORD = "admin123"  # You can change this

# # ---------------- LOGIN (Email only for users, password for admin) ----------------
# @auth_bp.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         email = request.form["email"]
#         password = request.form.get("password", "")
        
#         conn = get_db_connection()
#         if conn is None:
#             return render_template("login.html", error="Database connection failed")

#         cursor = conn.cursor(dictionary=True)
        
#         # Check if it's admin login
#         if email == ADMIN_EMAIL:
#             if password == ADMIN_PASSWORD:
#                 # Admin login successful
#                 session["user_id"] = 999  # Special admin ID
#                 session["user_name"] = "SJC Trichy Admin"
#                 session["user_email"] = ADMIN_EMAIL
#                 session["role"] = "admin"
                
#                 flash(f"Welcome Admin! 👨‍💼", "success")
#                 cursor.close()
#                 conn.close()
#                 return redirect(url_for("admin_bp.dashboard"))
#             else:
#                 cursor.close()
#                 conn.close()
#                 return render_template("login.html", error="Invalid admin password")
        
#         # Regular user login - just check if user exists by email
#         cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
#         user = cursor.fetchone()

#         cursor.close()
#         conn.close()

#         if user:
#             # User login successful
#             session["user_id"] = user["id"]
#             session["user_name"] = user["name"]
#             session["user_email"] = user["email"]
#             session["role"] = user["role"]

#             flash(f"Welcome back, {user['name']}! 🎉", "success")

#             return redirect(url_for("menu_bp.menu"))
#         else:
#             return render_template("login.html", error="Email not found. Please register first.")

#     return render_template("login.html")


# # ---------------- REGISTER (Simplified - only email and name) ----------------
# @auth_bp.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         name = request.form["name"]
#         email = request.form["email"]

#         # Basic validation
#         if not name or not email:
#             return render_template("register.html", error="Name and email are required")
        
#         if '@' not in email:
#             return render_template("register.html", error="Please enter a valid email address")
        
#         # Prevent registering with admin email
#         if email == ADMIN_EMAIL:
#             return render_template("register.html", error="This email is reserved for admin")

#         conn = get_db_connection()
#         if conn is None:
#             return render_template("register.html", error="Database connection failed")

#         cursor = conn.cursor(dictionary=True)

#         # Check if email already exists
#         cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
#         existing_user = cursor.fetchone()
        
#         if existing_user:
#             cursor.close()
#             conn.close()
#             return render_template("register.html", error="Email already registered. Please login.")

#         # Generate a simple random password (since your table might have password column)
#         random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        
#         # All new users are regular users (not admin)
#         role = 'user'

#         try:
#             # Insert new user
#             cursor.execute(
#                 "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
#                 (name, email, random_password, role)
#             )
#             conn.commit()
            
#             # Get the new user
#             cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
#             user = cursor.fetchone()
            
#             cursor.close()
#             conn.close()

#             if user:
#                 # Auto-login after registration
#                 session["user_id"] = user["id"]
#                 session["user_name"] = user["name"]
#                 session["user_email"] = user["email"]
#                 session["role"] = user["role"]
                
#                 flash(f"Welcome to SJC Trichy Canteen, {name}! 🎉", "success")
                
#                 return redirect(url_for("menu_bp.menu"))
#             else:
#                 return render_template("register.html", error="Registration failed. Please try again.")
                
#         except Exception as e:
#             print(f"Registration error: {e}")
#             conn.rollback()
#             cursor.close()
#             conn.close()
#             return render_template("register.html", error="Registration failed. Please try again.")

#     return render_template("register.html")


# # ---------------- LOGOUT ----------------
# @auth_bp.route("/logout")
# def logout():
#     session.clear()
#     flash("You have been logged out successfully", "info")
#     return redirect(url_for("auth_bp.login"))


# # ---------------- CHECK SESSION (API) ----------------
# @auth_bp.route("/api/check-session")
# def check_session():
#     if "user_id" in session:
#         return jsonify({
#             "logged_in": True,
#             "user_id": session["user_id"],
#             "user_name": session.get("user_name"),
#             "role": session.get("role")
#         })
#     else:
#         return jsonify({"logged_in": False})


# # ---------------- GET ALL USERS (Admin only) ----------------
# @auth_bp.route("/api/users")
# def get_users():
#     if session.get("role") != "admin":
#         return jsonify({"error": "Unauthorized"}), 401
    
#     conn = get_db_connection()
#     if conn is None:
#         return jsonify({"error": "Database connection failed"}), 500
    
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("SELECT id, name, email, role, created_at FROM users ORDER BY created_at DESC")
#     users = cursor.fetchall()
#     cursor.close()
#     conn.close()
    
#     return jsonify({"success": True, "users": users})




from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from backend.database.db_config import get_db_connection
import random
import string

auth_bp = Blueprint(
    "auth_bp",
    __name__,
    template_folder="../../frontend/templates"
)

# Admin credentials (hardcoded for demo)
ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "admin123"


# ---------------- LOGIN ----------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form.get("password", "")
        
        conn = get_db_connection()
        if conn is None:
            return render_template("login.html", error="Database connection failed")

        cursor = conn.cursor()   # ✅ FIXED (Removed dictionary=True)

        # Admin login
        if email == ADMIN_EMAIL:
            if password == ADMIN_PASSWORD:
                session["user_id"] = 999
                session["user_name"] = "SJC Trichy Admin"
                session["user_email"] = ADMIN_EMAIL
                session["role"] = "admin"

                flash("Welcome Admin! 👨‍💼", "success")
                cursor.close()
                conn.close()
                return redirect(url_for("admin_bp.dashboard"))
            else:
                cursor.close()
                conn.close()
                return render_template("login.html", error="Invalid admin password")

        # Regular user login
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]
            session["role"] = user["role"]

            flash(f"Welcome back, {user['name']}! 🎉", "success")
            return redirect(url_for("menu_bp.menu"))
        else:
            return render_template("login.html", error="Email not found. Please register first.")

    return render_template("login.html")


# ---------------- REGISTER ----------------
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]

        if not name or not email:
            return render_template("register.html", error="Name and email are required")

        if '@' not in email:
            return render_template("register.html", error="Please enter a valid email address")

        if email == ADMIN_EMAIL:
            return render_template("register.html", error="This email is reserved for admin")

        conn = get_db_connection()
        if conn is None:
            return render_template("register.html", error="Database connection failed")

        cursor = conn.cursor()   # ✅ FIXED

        cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            conn.close()
            return render_template("register.html", error="Email already registered. Please login.")

        random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        role = 'user'

        try:
            cursor.execute(
                "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
                (name, email, random_password, role)
            )
            conn.commit()

            cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
            user = cursor.fetchone()

            cursor.close()
            conn.close()

            if user:
                session["user_id"] = user["id"]
                session["user_name"] = user["name"]
                session["user_email"] = user["email"]
                session["role"] = user["role"]

                flash(f"Welcome to SJC Trichy Canteen, {name}! 🎉", "success")
                return redirect(url_for("menu_bp.menu"))
            else:
                return render_template("register.html", error="Registration failed. Please try again.")

        except Exception as e:
            print("Registration error:", e)
            conn.rollback()
            cursor.close()
            conn.close()
            return render_template("register.html", error="Registration failed. Please try again.")

    return render_template("register.html")


# ---------------- LOGOUT ----------------
@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully", "info")
    return redirect(url_for("auth_bp.login"))


# ---------------- CHECK SESSION ----------------
@auth_bp.route("/api/check-session")
def check_session():
    if "user_id" in session:
        return jsonify({
            "logged_in": True,
            "user_id": session["user_id"],
            "user_name": session.get("user_name"),
            "role": session.get("role")
        })
    else:
        return jsonify({"logged_in": False})


# ---------------- GET ALL USERS (Admin) ----------------
@auth_bp.route("/api/users")
def get_users():
    if session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor()   # ✅ FIXED
    cursor.execute("SELECT id, name, email, role FROM users ORDER BY id DESC")
    users = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({"success": True, "users": users})