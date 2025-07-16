import requests
import json
from datetime import datetime
import time

API_KEY = '005b8a3887ac4870920d909a7e31c7c5'
BASE_URL = 'http://api.football-data.org/v4'
HEADERS = {'X-Auth-Token': API_KEY}
REQUEST_DELAY = 6.1  # Задержка между запросами в секундах

# Статичный список лиг
LEAGUES = {
    'PL': 'Premier League',
    'PD': 'La Liga',
    'BL1': 'Bundesliga',
    'SA': 'Serie A',
    'FL1': 'Ligue 1',
    'PPL': 'Primeira Liga',
    'BSA': 'Brasileirão'
}

def save_data(data, filename='football_data.json'):
    """Сохранение данных в файл"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def make_request(url, params=None):
    """Безопасный запрос с задержкой"""
    time.sleep(REQUEST_DELAY)
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            retry_after = int(e.response.headers.get('Retry-After', 60))
            print(f"Достигнут лимит. Ждем {retry_after} секунд...")
            time.sleep(retry_after)
            return make_request(url, params)
        print(f"Ошибка запроса {url}: {e}")
        return None
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

def get_teams(league_code):
    """Получение списка команд лиги"""
    url = f"{BASE_URL}/competitions/{league_code}/teams"
    response = make_request(url)
    return response.json()['teams'] if response else []

def get_matches(league_code):
    """Получение матчей лиги"""
    url = f"{BASE_URL}/competitions/{league_code}/matches"
    response = make_request(url)
    return response.json()['matches'] if response else []

def update_team_stats(stats, match):
    """Обновление статистики команд"""
    home_team = match['homeTeam']['name']
    away_team = match['awayTeam']['name']
    
    if home_team not in stats:
        stats[home_team] = {'matches': 0, 'goals': 0}
    if away_team not in stats:
        stats[away_team] = {'matches': 0, 'goals': 0}
    
    if 'score' in match and 'fullTime' in match['score']:
        home_goals = match['score']['fullTime']['home'] or 0
        away_goals = match['score']['fullTime']['away'] or 0
        
        stats[home_team]['matches'] += 1
        stats[home_team]['goals'] += home_goals
        stats[away_team]['matches'] += 1
        stats[away_team]['goals'] += away_goals

def update_all_data():
    """Основная функция сбора данных"""
    all_matches = []
    team_stats = {}
    all_teams = {}
    
    for code, name in LEAGUES.items():
        print(f"Обработка лиги: {name}")
        
        # Получаем команды
        teams = get_teams(code)
        all_teams[code] = teams
        
        # Получаем матчи
        matches = get_matches(code)
        all_matches.extend(matches)
        
        # Собираем статистику
        for match in matches:
            update_team_stats(team_stats, match)
    
    # Сохраняем данные
    save_data({
        'leagues': LEAGUES,
        'teams': all_teams,
        'matches': all_matches,
        'stats': team_stats,
        'last_updated': datetime.now().isoformat()
    })
    
    print(f"Успешно! Обработано матчей: {len(all_matches)}")

if __name__ == "__main__":
    update_all_data()
