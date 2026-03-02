# from flask import Blueprint, render_template, session, redirect, url_for
# from backend.database.db_config import get_db_connection

# menu_bp = Blueprint("menu_bp", __name__)

# # ---------------- MENU PAGE ----------------
# @menu_bp.route("/menu")
# def menu():
#     # 🔐 User must be logged in
#     if "user_id" not in session:
#         return redirect(url_for("auth_bp.login"))

#     conn = get_db_connection()
#     if conn is None:
#         return render_template(
#             "menu.html",
#             products=[],
#             error="Database connection failed"
#         )

#     cursor = conn.cursor(dictionary=True)

#     try:
#         cursor.execute("SELECT * FROM products")
#         products = cursor.fetchall()
#     except Exception as e:
#         print("❌ Products fetch error:", e)
#         products = []
#     finally:
#         cursor.close()
#         conn.close()

#     return render_template("menu.html", products=products)



from flask import Blueprint, render_template, session, redirect, url_for
from backend.database.db_config import get_db_connection

menu_bp = Blueprint("menu_bp", __name__)

# ---------------- MENU PAGE ----------------
@menu_bp.route("/menu")
def menu():
    # 🔐 User must be logged in
    if "user_id" not in session:
        return redirect(url_for("auth_bp.login"))

    conn = get_db_connection()
    if conn is None:
        return render_template(
            "menu.html",
            products=[],
            error="Database connection failed"
        )

    cursor = conn.cursor()   # ✅ FIXED (Removed dictionary=True)

    try:
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
    except Exception as e:
        print("❌ Products fetch error:", e)
        products = []
    finally:
        cursor.close()
        conn.close()

    return render_template("menu.html", products=products)
