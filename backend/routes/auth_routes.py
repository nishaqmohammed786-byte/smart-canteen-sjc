from flask import Blueprint, render_template, request, redirect, url_for, session
from backend.database.db_config import get_db_connection

auth_bp = Blueprint(
    "auth_bp",
    __name__,
    template_folder="../../frontend/templates"
)

# ---------------- LOGIN ----------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        if conn is None:
            return render_template(
                "login.html",
                error="Database connection failed. Please start MySQL."
            )

        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["role"] = user["role"]

            if user["role"] == "admin":
                return redirect(url_for("admin_bp.dashboard"))
            else:
                return redirect(url_for("menu_bp.menu"))

        return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")


# ---------------- REGISTER ----------------
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        if conn is None:
            return render_template(
                "register.html",
                error="Database connection failed. Please start MySQL."
            )

        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return render_template("register.html", error="Email already exists")

        cursor.execute(
            "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, 'user')",
            (name, email, password)
        )
        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for("auth_bp.login"))

    return render_template("register.html")


# ---------------- LOGOUT ----------------
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth_bp.login"))
