import os
import requests
import sqlite3
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pytz

# Настройка путей
BASE_DIR = "/storage/emulated/0/football-predictor"
DB_PATH = os.path.join(BASE_DIR, "database/football.db")
ENV_PATH = os.path.join(BASE_DIR, ".env")

# Загрузка конфигурации
load_dotenv(ENV_PATH)
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
BASE_URL = "http://api.openweathermap.org/data/2.5"

def get_db_connection():
    return sqlite3.connect(DB_PATH)

def get_stadium_location(team_id):
    """Получаем координаты стадиона из БД"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT stadium FROM teams WHERE api_id = ?", (team_id,))
    result = cursor.fetchone()
    conn.close()
    
    # Заглушка - в реальности нужно преобразовывать название стадиона в координаты
    # Здесь используем координаты Лужников как пример
    return (55.715765, 37.554272) if result else (55.7558, 37.6176)  # Москва по умолчанию

def fetch_weather(lat, lon, match_time):
    """Получение прогноза погоды"""
    url = f"{BASE_URL}/onecall/timemachine"
    
    params = {
        'lat': lat,
        'lon': lon,
        'dt': int(match_time.timestamp()),
        'units': 'metric',
        'lang': 'ru',
        'appid': WEATHER_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Ошибка при запросе погоды: {e}")
        return None

def save_weather_to_db(match_id, weather_data):
    """Сохранение погодных данных в БД"""
    if not weather_data or 'current' not in weather_data:
        return False
    
    current = weather_data['current']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT OR REPLACE INTO weather (
            match_id, temperature, humidity, wind_speed, 
            wind_direction, pressure, weather_code, conditions
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            match_id,
            current['temp'],
            current['humidity'],
            current['wind_speed'],
            current.get('wind_deg', 'N/A'),
            current.get('pressure', 0),
            current['weather'][0]['id'],
            current['weather'][0]['description']
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"Ошибка при сохранении погоды: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def process_upcoming_matches():
    """Обработка предстоящих матчей"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Берем матчи на следующие 3 дня
    start_date = datetime.now()
    end_date = start_date + timedelta(days=3)
    
    cursor.execute('''
    SELECT m.id, m.api_id, m.home_team_id, m.match_date 
    FROM matches m
    LEFT JOIN weather w ON m.id = w.match_id
    WHERE m.status = 'scheduled'
    AND m.match_date BETWEEN ? AND ?
    AND w.match_id IS NULL
    ''', (start_date.isoformat(), end_date.isoformat()))
    
    matches = cursor.fetchall()
    conn.close()
    
    for match in matches:
        match_id, api_id, home_team_id, match_time_str = match
        match_time = datetime.fromisoformat(match_time_str)
        
        # Получаем местоположение стадиона
        lat, lon = get_stadium_location(home_team_id)
        
        # Получаем погоду
        weather_data = fetch_weather(lat, lon, match_time)
        
        if weather_data:
            if save_weather_to_db(match_id, weather_data):
                print(f"Сохранена погода для матча {api_id}")
            else:
                print(f"Не удалось сохранить погоду для матча {api_id}")
        else:
            print(f"Не удалось получить погоду для матча {api_id}")

if __name__ == '__main__':
    # Установите временную зону (для серверов важно)
    os.environ['TZ'] = 'Europe/Moscow'
    
    # Проверяем API ключ
    if not WEATHER_API_KEY:
        print("Ошибка: не задан WEATHER_API_KEY в .env")
    else:
        print("Старт сбора погодных данных...")
        process_upcoming_matches()
        print("Завершено!")
