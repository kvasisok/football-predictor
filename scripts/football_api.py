import os
import requests
import sqlite3
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Настройка путей
BASE_DIR = "/storage/emulated/0/football-predictor"
DB_PATH = os.path.join(BASE_DIR, "database/football.db")
ENV_PATH = os.path.join(BASE_DIR, ".env")

# Загрузка конфигурации
load_dotenv(ENV_PATH)
API_KEY = os.getenv("FOOTBALL_API_KEY")
BASE_URL = "https://api.football-data.org/v4"

HEADERS = {
    "X-Auth-Token": API_KEY,
    "Content-Type": "application/json"
}

def get_db_connection():
    return sqlite3.connect(DB_PATH)

def fetch_competitions():
    """Получение списка лиг"""
    url = f"{BASE_URL}/competitions"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Ошибка при запросе лиг: {e}")
        return None

def fetch_teams(competition_id, season=None):
    """Получение команд лиги"""
    season = season or datetime.now().year
    url = f"{BASE_URL}/competitions/{competition_id}/teams?season={season}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Ошибка при запросе команд: {e}")
        return None

def fetch_matches(competition_id, date_from=None, date_to=None):
    """Получение матчей лиги"""
    date_from = date_from or datetime.now().strftime("%Y-%m-%d")
    date_to = date_to or (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    
    url = f"{BASE_URL}/competitions/{competition_id}/matches"
    params = {
        "dateFrom": date_from,
        "dateTo": date_to
    }
    
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Ошибка при запросе матчей: {e}")
        return None

def save_to_database(data, data_type):
    """Сохранение данных в БД"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if data_type == "teams":
            for team in data.get('teams', []):
                cursor.execute('''
                INSERT OR REPLACE INTO teams (
                    api_id, name, short_name, country, founded, 
                    stadium, strength_attack, strength_defense, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    team['id'],
                    team['name'],
                    team.get('shortName', ''),
                    team.get('area', {}).get('name', ''),
                    team.get('founded', None),
                    team.get('venue', ''),
                    team.get('strength', {}).get('attack', 0),
                    team.get('strength', {}).get('defense', 0),
                    datetime.now().isoformat()
                ))
        
        elif data_type == "matches":
            for match in data.get('matches', []):
                cursor.execute('''
                INSERT OR REPLACE INTO matches (
                    api_id, home_team_id, away_team_id, league, season,
                    match_date, status, home_score, away_score, stats_json,
                    odds_home, odds_draw, odds_away
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    match['id'],
                    match['homeTeam']['id'],
                    match['awayTeam']['id'],
                    match['competition']['name'],
                    match['season']['startDate'][:4],
                    match['utcDate'],
                    match['status'],
                    match['score'].get('fullTime', {}).get('home', None),
                    match['score'].get('fullTime', {}).get('away', None),
                    json.dumps(match.get('stats', {})),
                    match['odds'].get('homeWin', None) if 'odds' in match else None,
                    match['odds'].get('draw', None) if 'odds' in match else None,
                    match['odds'].get('awayWin', None) if 'odds' in match else None
                ))
        
        conn.commit()
    except Exception as e:
        print(f"Ошибка при сохранении в БД: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    # Пример использования
    leagues = fetch_competitions()
    if leagues:
        print(f"Доступно лиг: {len(leagues['competitions'])}")
        
        # Для примера - берем первую лигу
        league_id = leagues['competitions'][0]['id']
        
        teams_data = fetch_teams(league_id)
        if teams_data:
            save_to_database(teams_data, "teams")
            print(f"Сохранено команд: {len(teams_data['teams'])}")
        
        matches_data = fetch_matches(league_id)
        if matches_data:
            save_to_database(matches_data, "matches")
            print(f"Сохранено матчей: {len(matches_data['matches'])}")
