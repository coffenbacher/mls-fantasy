import json
import requests
from bs4 import BeautifulSoup
import re
import os
import logging; logging.basicConfig(); log = logging.getLogger(); log.setLevel('INFO')
#
def extract_game_logs(new=True):
    seasons = range(int(os.getenv('START_YEAR', 2014)), 2020)
    urls = []
    for s in seasons:
        for comp_type in (44, 45, 46):
            u = 'http://www.mlssoccer.com/schedule?month=all&year=%s&competition_type=%s' % (s, comp_type)
            log.info('Processing season %s' % u)
            page = BeautifulSoup(requests.get(u).content)
            links = page.find_all('a', text="MATCHCENTER", href=re.compile('.*matchcenter/20.*'))
            urls.extend([l['href'] for l in links])
    
    for url in urls:
        u = 'https://rawgit.com/coffenbacher/mls-data/master/automated/games/%s.json' % url.split('/')[-1]
        log.info('Checking for existence of %s' % u)
        exists = requests.get(u).status_code == 200
        if not exists or not new:
            data = extract_game_data(url)
            if data and data['action'] == 'recap':
                yield data

def extract_game_data(url):
    soup = BeautifulSoup(requests.get(url).content)
    elems = soup.find_all('script', text=re.compile('window.bootstrap'))
    if len(elems) != 1:
        return False
    data = json.loads(re.search('{.*}', elems[0].string).group(0))
    return data
    
if __name__ == '__main__':
    extract_game_logs()