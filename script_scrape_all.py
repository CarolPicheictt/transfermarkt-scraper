import subprocess
import json
import csv
import os

def load_competitions_csv(csv_path):
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return [row['competition_name'] for row in reader]

def filter_competitions(competitions_json, names):
    filtered = [comp for comp in competitions_json if comp.get('name') in names]
    return filtered

def run_scrape(crawler, output_file, parents=None, season=None):
    cmd = ['python', '-m', 'tfmkt', crawler]
    if season is not None:
        cmd.extend(['-s', str(season)])
    if parents is not None:
        cmd.extend(['-p', parents])
    with open(output_file, 'w', encoding='utf-8') as f:
        subprocess.run(cmd, stdout=f, text=True)

# Primeiro, scrapear competitions
print("Scraping competitions...")
run_scrape('competitions', 'competitions.json')

# Carregar e filtrar
with open('competitions.json', 'r', encoding='utf-8') as f:
    competitions = [json.loads(line) for line in f]

names = load_competitions_csv('competicoes_selecoes_masculinas.csv')
filtered = filter_competitions(competitions, names)

with open('filtered_competitions.json', 'w', encoding='utf-8') as f:
    for item in filtered:
        json.dump(item, f, ensure_ascii=False)
        f.write('\n')

# Agora, para cada crawler
crawlers_with_season = ['games', 'appearances', 'clubs', 'players', 'national_team_competitions']
crawlers_without_season = ['tournament_editions']
crawlers_no_parents = ['confederations']

for crawler in crawlers_no_parents:
    print(f"Scraping {crawler}...")
    run_scrape(crawler, f'{crawler}.json')

for crawler in crawlers_without_season:
    print(f"Scraping {crawler}...")
    run_scrape(crawler, f'{crawler}.json', parents='filtered_competitions.json')

for crawler in crawlers_with_season:
    print(f"Scraping {crawler} for seasons 1930-2026...")
    for season in range(2020, 2027):
        print(f"  Season {season}...")
        run_scrape(crawler, f'{crawler}_{season}.json', parents='filtered_competitions.json', season=season)

print("Scraping complete.")