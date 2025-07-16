import os
from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

# Определяем путь к БД в зависимости от окружения
DB_PATH = "/tmp/football.db" if 'VERCEL' in os.environ else "database/football.db"

def init_db():
    """Инициализация БД при первом запуске"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY,
            home_team TEXT,
            away_team TEXT,
            match_date TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return "Football Predictor on Vercel - Ready!"

@app.route('/api/matches')
def matches():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM matches LIMIT 10")
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
