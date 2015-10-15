#!/usr/bin/env python
#Author: Dimitry Slavin (BUT not wholly my own code, read notes below)
#Name: "get_players.py"
#Date Created: March 2015 (Estimated)
#Notes: This is not wholly my own code. This is a tweaked version of Daniel Rodriguez's code.
#Link to Daniel Rodriguez's blog post: http://danielfrg.com/blog/2013/04/01/nba-scraping-data/
#General Purpose: Scrape NBA player statistics from ESPN for each game of the 2004-05 to 2014-15 seasons. 
#Detailed Purpose (Enumerated): None

import numpy as np
import pandas as pd
import requests
import traceback
from bs4 import BeautifulSoup
from datetime import datetime, date

games = pd.read_csv('games.csv')
BASE_URL = 'http://espn.go.com/nba/boxscore?gameId={0}'
r = requests.get(BASE_URL.format(games.index[0]))
text1 = BeautifulSoup(r.text)
#master_keys = ['match_id', 'team', 'player_id', 'player'] + \
        #['MIN','FGM-A','3PM-A','FTM-A','OREB','DREB','REB','AST',
        #'STL','BLK','TO','PF','+/-','PTS']

ind_count = 0
players = pd.DataFrame()
match_ids = [mid for mid in games['match_id']]

def split_column(dfseries,split_char,var_name):
    new_names = var_name.split(split_char)
    seriesa = []
    seriesb = []
    for item in dfseries:
        if not str(item) == 'nan':
            seriesa.append(str(item).split(split_char)[0]) 
            seriesb.append(str(item).split(split_char)[1])
        else:
            seriesa.append(np.nan)
            seriesb.append(np.nan)
    
    seriesa = pd.Series(seriesa, index = dfseries.index, name = new_names[0])
    seriesb = pd.Series(seriesb, index = dfseries.index, name = new_names[0][0:-1]+new_names[1])
    split_df = pd.concat([seriesa, seriesb], axis=1)
    
    return split_df


def get_player_dicts(players, team_name, keys, index):
    player_dicts = []
    for player in players:
        values = []
        values.append(index) #adds match_id
        try:
            cols = player.find_all('td')
            values.append(team_name) #adds team name
            pdata = cols[0].a['href'].split('id/')[-1].split('/')
            values.append(pdata[0]) #adds player id
            values.append(pdata[1]) #adds player name
            for stat in cols[1::]:
                if not cols[1].text.startswith('DNP'):
                    values.append(stat.text)
            #print values
            player_dict = dict(zip(keys, values))
            player_dicts.append(player_dict)
        except Exception as e:
            print traceback.format_exc()

    pframe = pd.DataFrame(player_dicts)
    return pframe


for index in match_ids:
    ind_count += 1
    #if ind_count > 20:
      #  break
    print(index)
    try:
        r = requests.get(BASE_URL.format(index))
        text1 = BeautifulSoup(r.text)
        heads = text1.find_all('thead')
        keys = ['match_id', 'team', 'player_id', 'player']+[item.text for item in heads[0].find_all('th')[2::]]
        bodies = text1.find_all('tbody')

        team_1 = heads[0].th.text
        team_1_players = bodies[0].find_all('tr') + bodies[1].find_all('tr')
        team_1_players = get_player_dicts(team_1_players, team_1, keys, index)
        players = players.append(team_1_players)

        team_2 = heads[3].th.text
        team_2_players = bodies[3].find_all('tr') + bodies[4].find_all('tr')
        team_2_players = get_player_dicts(team_2_players, team_2, keys, index)
        players = players.append(team_2_players)

    except Exception as e:
        print traceback.format_exc()
        #pass # Not all columns row are a match, is OK
                # print(e)

players = players.set_index('match_id')
print players

to_split = ['3PM-A','FGM-A','FTM-A']
for name in to_split:
    split_df = split_column(players[name],'-',name)
    players = pd.concat([players,split_df],axis = 1)
    del players[name]

new_keys = ['player','player_id','team','AST', 'BLK','DREB', 'MIN', 'OREB','PF', '+/-','PTS', 'REB',
    'STL', 'TO', '3PM', '3PA', 'FGM', 'FGA', 'FTM', 'FTA']

players = players[new_keys]
players.to_csv("players.csv")