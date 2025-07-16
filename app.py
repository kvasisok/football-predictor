import os
from flask import Flask, render_template, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Путь к БД (на Vercel используем /tmp, локально - в папке проекта)
DB_PATH = "/tmp/football.db" if 'VERCEL' in os.environ else os.path.join(os.path.dirname(os.path.abspath(__file__)), "database/football.db")

def init_db():
    """Инициализация базы данных"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY,
        home_team TEXT,
        away_team TEXT,
        match_date TEXT,
        league TEXT,
        home_score INTEGER,
        away_score INTEGER
    )''')
    
    # Добавляем тестовые данные, если таблица пуста
    cursor.execute("SELECT COUNT(*) FROM matches")
    if cursor.fetchone()[0] == 0:
        test_matches = [
            ("Team A", "Team B", datetime.now().isoformat(), "Premier League", None, None),
            ("Team C", "Team D", datetime.now().isoformat(), "La Liga", None, None)
        ]
        cursor.executemany(
            "INSERT INTO matches (home_team, away_team, match_date, league, home_score, away_score) VALUES (?, ?, ?, ?, ?, ?)",
            test_matches
        )
    conn.commit()
    conn.close()

@app.route('/')
def home():
    """Главная страница"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM matches ORDER BY match_date DESC LIMIT 10")
    matches = cursor.fetchall()
    conn.close()
    return render_template('index.html', matches=matches)

@app.route('/api/matches')
def api_matches():
    """JSON API для матчей"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM matches ORDER BY match_date DESC LIMIT 10")
    matches = cursor.fetchall()
    conn.close()
    
    # Преобразуем в словарь для JSON
    result = []
    for match in matches:
        result.append({
            'id': match[0],
            'home_team': match[1],
            'away_team': match[2],
            'date': match[3],
            'league': match[4],
            'score': f"{match[5] or '-'}:{match[6] or '-'}"
        })
    return jsonify(result)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
