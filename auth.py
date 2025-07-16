from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
import sqlite3
import os

# Настройки
BASE_DIR = "/storage/emulated/0/football-predictor"
DB_PATH = os.path.join(BASE_DIR, "database/football.db")

# Создаем Blueprint (можно подключить к основному app.py)
auth_bp = Blueprint('auth', __name__)

# Конфигурация Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

class User(UserMixin):
    def __init__(self, id_, username):
        self.id = id_
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users WHERE id = ?", (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    if user_data:
        return User(id_=user_data[0], username=user_data[1])
    return None

# Роуты аутентификации
@auth_bp.route('/login')
def login():
    return render_template('auth/login.html')

@auth_bp.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
    user_data = cursor.fetchone()
    conn.close()
    
    if not user_data or not check_password_hash(user_data[2], password):
        flash('Неверные данные!')
        return redirect(url_for('auth.login'))
    
    user = User(id_=user_data[0], username=user_data[1])
    login_user(user)
    return redirect(url_for('main.index'))

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

# Функция для инициализации (вызвать из app.py при необходимости)
def init_auth(app):
    login_manager.init_app(app)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Создаем таблицу пользователей, если её нет
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

# Пример добавления тестового пользователя (выполнить один раз)
# def create_test_user():
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
#     cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)",
#                    ('admin', generate_password_hash('admin123')))
#     conn.commit()
#     conn.close()
