import sqlite3
import os
from datetime import datetime

# Пути к файлам
BASE_DIR = "/storage/emulated/0/football-predictor"
DB_PATH = os.path.join(BASE_DIR, "database/football.db")

def init_database():
    # Создаем папку database, если её нет
    os.makedirs(os.path.join(BASE_DIR, "database"), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Таблица команд (дополненная структура)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY,
        api_id INTEGER UNIQUE,  # ID из внешнего API
        name TEXT NOT NULL,
        short_name TEXT,
        country TEXT,
        founded INTEGER,
        stadium TEXT,
        strength_attack INTEGER,
        strength_defense INTEGER,
        last_updated TIMESTAMP
    )''')
    
    # Таблица матчей (расширенная версия)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY,
        api_id INTEGER UNIQUE,
        home_team_id INTEGER,
        away_team_id INTEGER,
        league TEXT NOT NULL,
        season TEXT,
        match_date TIMESTAMP NOT NULL,
        status TEXT CHECK(status IN ('scheduled', 'live', 'finished')),
        home_score INTEGER,
        away_score INTEGER,
        stats_json TEXT,  # JSON с детальной статистикой
        odds_home REAL,
        odds_draw REAL,
        odds_away REAL,
        FOREIGN KEY (home_team_id) REFERENCES teams(id),
        FOREIGN KEY (away_team_id) REFERENCES teams(id)
    )''')
    
    # Улучшенная таблица погоды
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS weather (
        id INTEGER PRIMARY KEY,
        match_id INTEGER UNIQUE,
        temperature REAL,
        humidity INTEGER,
        wind_speed REAL,
        wind_direction TEXT,
        pressure INTEGER,
        weather_code INTEGER,
        conditions TEXT,
        precipitation REAL,
        visibility INTEGER,
        FOREIGN KEY (match_id) REFERENCES matches(id)
    )''')
    
    # Усложненная таблица прогнозов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY,
        match_id INTEGER UNIQUE,
        model_version TEXT NOT NULL,
        home_win_prob REAL NOT NULL,
        draw_prob REAL NOT NULL,
        away_win_prob REAL NOT NULL,
        recommended_bet TEXT,
        confidence REAL,
        features_json TEXT,  # JSON с использованными фичами
        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (match_id) REFERENCES matches(id)
    )''')
    
    # Таблица для кэширования запросов API
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS api_cache (
        id INTEGER PRIMARY KEY,
        endpoint TEXT NOT NULL,
        parameters TEXT,
        response_json TEXT NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    conn.commit()
    conn.close()
    print(f"База данных создана по пути: {DB_PATH}")

if __name__ == '__main__':
    init_database()
