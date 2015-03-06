from persist import persist
from utils import extract_mls_fantasy_data

def main():
    results = extract_mls_fantasy_data()
    for r in results:
        persist(r['data'], r['fieldnames'], r['name'], project_name='mls-data')

if __name__ == '__main__':
    main()