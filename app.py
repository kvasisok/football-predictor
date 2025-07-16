import os
from flask import Flask, render_template, jsonify
import sqlite3
from datetime import datetime

# Конфигурация
BASE_DIR = "/storage/emulated/0/football-predictor"
DB_PATH = os.path.join(BASE_DIR, "database/football.db")

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    """Главная страница с предстоящими матчами"""
    db = get_db()
    matches = db.execute('''
        SELECT m.id, t1.name as home_team, t2.name as away_team, 
               m.match_date, m.league, p.home_win_prob, 
               p.draw_prob, p.away_win_prob
        FROM matches m
        JOIN teams t1 ON m.home_team_id = t1.api_id
        JOIN teams t2 ON m.away_team_id = t2.api_id
        LEFT JOIN predictions p ON m.id = p.match_id
        WHERE m.status = 'scheduled'
        ORDER BY m.match_date
        LIMIT 20
    ''').fetchall()
    db.close()
    return render_template('index.html', matches=matches)

@app.route('/api/matches')
def api_matches():
    """JSON API для матчей"""
    db = get_db()
    matches = db.execute('''
        SELECT m.id, t1.name as home_team, t2.name as away_team,
               m.match_date, m.league, m.home_score, m.away_score
        FROM matches m
        JOIN teams t1 ON m.home_team_id = t1.api_id
        JOIN teams t2 ON m.away_team_id = t2.api_id
        ORDER BY m.match_date DESC
        LIMIT 50
    ''').fetchall()
    db.close()
    return jsonify([dict(match) for match in matches])

@app.route('/match/<int:match_id>')
def match_detail(match_id):
    """Страница матча с детальной статистикой"""
    db = get_db()
    match = db.execute('''
        SELECT m.*, t1.name as home_team, t2.name as away_team,
               w.temperature, w.conditions, p.*
        FROM matches m
        JOIN teams t1 ON m.home_team_id = t1.api_id
        JOIN teams t2 ON m.away_team_id = t2.api_id
        LEFT JOIN weather w ON m.id = w.match_id
        LEFT JOIN predictions p ON m.id = p.match_id
        WHERE m.id = ?
    ''', (match_id,)).fetchone()
    db.close()
    return render_template('match.html', match=match)

if __name__ == '__main__':
    # Запуск на порту 8080 для Termux
    app.run(host='0.0.0.0', port=8080, debug=True)
