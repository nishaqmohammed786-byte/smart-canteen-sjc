# from flask import Blueprint, redirect, url_for

# main_bp = Blueprint('main_bp', __name__)

# @main_bp.route('/')
# def home():
#     return redirect(url_for('menu_bp.all_menu'))


from flask import Blueprint, redirect, url_for

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def home():
    return redirect(url_for('menu_bp.menu'))