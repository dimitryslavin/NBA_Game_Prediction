#!/usr/bin/env python
#Author: Dimitry Slavin (BUT not wholly my own code, read notes below)
#Name: "get_games.py"
#Date Created: March 2015 (Estimated)
#Notes: This is not my own code. This is a tweaked version of Daniel Rodriguez's code.
#Link to Daniel Rodriguez's blog post: http://danielfrg.com/blog/2013/04/01/nba-scraping-data/
#General Purpose: Scrape NBA game statistics from ESPN for the 2004-05 to 2014-15 seasons. 
#Detailed Purpose (Enumerated): None

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date

gamesDict = []
keys = ['match_id', 'date', 'home_team', 'home_team_score', 'visit_team', 
        'visit_team_score', 'season', 'hi_points', 'hi_points_pid', 
        'hi_points_pname','hi_rebs','hi_rebs_pid', 'hi_rebs_pname', 
        'hi_asts', 'hi_asts_pid','hi_asts_pname']
years = range(2005,2016)

for year in years:
    teams = pd.read_csv('teams_and_prefixes.csv')
    BASE_URL = 'http://espn.go.com/nba/team/schedule/_/name/{0}/year/{1}/{2}'

    for index, row in teams.iterrows():
        _team, url = row['team'], row['url']
        r = requests.get(BASE_URL.format(row['prefix_1'], year, row['prefix_2']))
        table = BeautifulSoup(r.text).table
        if table is None:
            continue
        for row in table.find_all('tr')[1:]: # Remove header
            columns = row.find_all('td')
            try:
                _home = True if columns[1].li.text == 'vs' else False
                _other_team = columns[1].find_all('a')[1].text
                _score = columns[2].a.text.split(' ')[0].split('-')
                _won = True if columns[2].span.text == 'W' else False
                _hipoints_pdata = columns[4].a['href'].split('id/')[-1].split('/')
                _hirebs_pdata = columns[5].a['href'].split('id/')[-1].split('/')
                _hiasts_pdata = columns[6].a['href'].split('id/')[-1].split('/')

                match_id = columns[2].a['href'].split('?id=')[1]
                d = datetime.strptime(columns[0].text, '%a, %b %d')
                if d.month > 9:
                    date1 = date(year-1, d.month, d.day) 
                else:
                    date1 = date(year, d.month, d.day)
                home_team = _team if _home else _other_team
                visit_team = _team if not _home else _other_team
                season = year 
                hi_points = int(columns[4].text.split()[-1])
                hi_points_pid = int(_hipoints_pdata[0])
                hi_points_pname = _hipoints_pdata[-1]
                hi_rebs = int(columns[5].text.split()[-1])
                hi_rebs_pid = int(_hirebs_pdata[0])
                hi_rebs_pname = _hirebs_pdata[-1]
                hi_asts = int(columns[5].text.split()[-1])
                hi_asts_pid = int(_hiasts_pdata[0])
                hi_asts_pname = _hiasts_pdata[-1]

                if _home:
                    if _won:
                        home_team_score = _score[0]
                        visit_team_score = _score[1]
                    else:
                        home_team_score = _score[1] 
                        visit_team_score = _score[0]
                else:
                    if _won:
                        home_team_score = _score[1]
                        visit_team_score = _score[0]
                    else:
                        home_team_score = _score[0]
                        visit_team_score = _score[1]

                values = [match_id, date1, home_team, home_team_score, visit_team,
                          visit_team_score, season, hi_points, hi_points_pid, 
                          hi_points_pname,hi_rebs,hi_rebs_pid, hi_rebs_pname, 
                          hi_asts, hi_asts_pid,hi_asts_pname]
                game_dict = dict(zip(keys, values))
                gamesDict.append(game_dict)
            except Exception as e:
                pass # Not all columns row are a match, is OK
                # print(e)

games = pd.DataFrame(gamesDict).drop_duplicates(cols='match_id').set_index('match_id')
games.to_csv("games.csv")