import requests, sqlite3
from datetime import datetime

API_KEY = '005b8a3887ac4870920d909a7e31c7c5'
HEADERS = {'X-Auth-Token': API_KEY}

def log(message):
    with open("api_parser.log", "a") as f:
        f.write(f"{datetime.now()} | {message}\n")

def fetch_matches():
    try:
        response = requests.get(
            'https://api.football-data.org/v4/matches',
            headers=HEADERS,
            timeout=15
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        log(f"API Error: {str(e)}")
        return None

def parse_matches(data):
    matches = []
    for match in data.get('matches', []):
        try:
            # Основные данные
            date = match['utcDate'][:10]
            league = match['competition']['name']
            
            # Пропускаем не российские лиги (если нужно только РПЛ)
            if 'Russia' not in league:
                continue
                
            # Команды
            home = match['homeTeam'].get('shortName', 'Unknown')
            away = match['awayTeam'].get('shortName', 'Unknown')
            
            # Счет
            score_data = match.get('score', {})
            ft_score = score_data.get('fullTime', {})
            score = f"{ft_score.get('home', '?')}-{ft_score.get('away', '?')}" if ft_score else '0-0'
            
            matches.append((date, home, away, score, league))
        except KeyError as e:
            log(f"Parse error in match: {e}")
    return matches

def save_to_db(matches):
    conn = sqlite3.connect('football.db')
    c = conn.cursor()
    c.executemany("""
        INSERT OR REPLACE INTO matches 
        (date, home_team, away_team, score, league) 
        VALUES (?, ?, ?, ?, ?)
    """, matches)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    log("=== START PARSER ===")
    data = fetch_matches()
    if data:
        matches = parse_matches(data)
        if matches:
            save_to_db(matches)
            log(f"Added {len(matches)} matches")
            print(f"Успешно! Добавлено матчей РПЛ: {len(matches)}")
        else:
            log("No Russian matches found")
            print("Российские матчи не найдены")
    else:
        log("API request failed")
        print("Ошибка запроса к API")
