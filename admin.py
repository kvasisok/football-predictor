from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required
import sqlite3
import os

# Настройки
BASE_DIR = "/storage/emulated/0/football-predictor"
DB_PATH = os.path.join(BASE_DIR, "database/football.db")

# Создаем Blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Роуты админки
@admin_bp.route('/')
@login_required
def dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/matches')
@login_required
def manage_matches():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM matches ORDER BY match_date DESC LIMIT 50")
    matches = cursor.fetchall()
    conn.close()
    return render_template('admin/matches.html', matches=matches)

@admin_bp.route('/users')
@login_required
def manage_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users")
    users = cursor.fetchall()
    conn.close()
    return render_template('admin/users.html', users=users)

# Функция для инициализации (вызвать из app.py при необходимости)
def init_admin(app):
    app.register_blueprint(admin_bp)
