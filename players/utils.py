import json
import requests
from bs4 import BeautifulSoup
import re

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
    
    return results