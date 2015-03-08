from games.sync import extract_game_logs
from persist import persist

def sync_new_games():
    games = extract_game_logs(new=True)
    for g in games:
        persist(g, 'games', file_name=g['match']['slug'], project_name='mls-data', 
            write_meta=False, write_csv=False, auto_add_file=True)