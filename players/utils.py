import json
import StringIO
import requests
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
import re
import os
import csv

DELTA_KEYS = ['total_points','assists','big_chances_created','clean_sheets',
'clearances_blocks_interceptions','crosses',
'errors_leading_to_goal','goals_conceded','goals_scored','key_passes','minutes',
'own_goal_earned','own_goals','penalties_conceded','penalties_earned',
'penalties_missed','penalties_saved','recoveries','red_cards','saves',
'transfers_in','transfers_out','yellow_cards']

def extract_mls_fantasy_data():
    results = []
    res = json.loads(requests.get('http://fantasy.mlssoccer.com/drf/bootstrap').content)
    
    # Players
    players = res['elements']
    for p in players:
        p['photo'] = 'http://cdn.ismfg.net/static/mlsf/img/shirts/photos/%s' % p['photo']
        p['team_name'] = filter(lambda t: t['id'] == p['team'], res['teams'])[0]['name']
        p['position'] = filter(lambda e: e['id'] == p['element_type'], res['element_types'])[0]['singular_name']
        
    first_fields = ['id', 'web_name', 'first_name', 'second_name', 'team_name', 'position', 'total_points', 'now_cost',]
    fieldnames = first_fields + sorted(list(set(p.keys()).difference(first_fields)))
    results.append({'name': 'players', 'data': players, 'fieldnames': fieldnames})
    
    # Teams
    teams = res['teams']
    first_fields = ['id', 'name',]
    fieldnames = first_fields + sorted(list(set(teams[0].keys()).difference(first_fields)))
    fieldnames.remove('next_event_fixture')
    fieldnames.remove('current_event_fixture')
    results.append({'name': 'teams', 'data': teams, 'fieldnames': fieldnames})
    
    # Weekly summary
    try:
        results.append(summarize_weekly_data())
    except:
        pass
    
    return results
    
def summarize_weekly_data():
    d = parse('2015-03-02')
    
    t = os.getenv('TOKEN')
    data = []
    prev_week = []
    for i in range(34):
        game_week = i+1
        d = d + relativedelta(days=7)
        ds = d.strftime('%Y-%m-%d')
        u = 'https://api.github.com/repos/coffenbacher/mls-data/commits?until=%sT16:00:00Z&since=%sT13:00:00Z' % (d, d)
        r = requests.get(u, headers={'Authorization': 'token %s' % t})
        j = json.loads(r.content)
        if not j:
            break
        h = j[0]['sha']
        data_url = 'https://raw.githubusercontent.com/coffenbacher/mls-data/%s/automated/players/players.csv' % h
        c = requests.get(data_url).content
        week_file = StringIO.StringIO(c)
        week_dicts = list(csv.DictReader(week_file))
        # Get field names
        fieldnames = ['round'] + c.replace('"', '').split('\n')[0].split(',') + ['event_%s' % key for key in DELTA_KEYS]
        
        for w in week_dicts:
            w.update({'round': game_week})
            prev_rows = filter(lambda x: x['id'] == w['id'], prev_week)
            if prev_rows:
                for key in DELTA_KEYS:
                    w['event_%s' % key] = float(w[key]) - float(prev_rows[0][key])
            else:
                for key in DELTA_KEYS:
                    w['event_%s' % key] = float(w[key])
        prev_week = filter(lambda x: x.get('id'), week_dicts)
        data.extend(week_dicts)
        
    
    return {'name': 'weekly_snapshot', 'fieldnames': fieldnames, 'data': data}