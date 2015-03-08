from persist import persist
from utils import extract_mls_fantasy_data

def sync_players():
    results = extract_mls_fantasy_data()
    for r in results:
        persist(r['data'], r['name'], fieldnames=r['fieldnames'], project_name='mls-data')