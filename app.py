import os
from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

# Для Vercel: используем /tmp для SQLite (файловая система доступна только на запись здесь)
DB_PATH = "/tmp/football.db" if 'VERCEL' in os.environ else "/storage/emulated/0/football-predictor/database/football.db"

@app.route('/')
def home():
    return "Football Predictor on Vercel!"

@app.route('/api/matches')
def matches():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM matches LIMIT 10")
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
