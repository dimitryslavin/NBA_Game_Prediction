import numpy as np
import pandas as pd

teams = pd.read_csv('teams.csv')
games = pd.read_csv('games.csv',index_col = False)
players = pd.read_csv('players.csv', index_col = False)

games.date = pd.to_datetime([date1.split(' ')[0] for date1 in games.date], format='%Y-%m-%d')

games['home_team_id'] = None
games['visit_team_id'] = None
players['team_id'] = None
sorted_teams = sorted(teams.team.values)
for ind, team_name in enumerate(sorted_teams):
    games.loc[games.home_team == team_name, 'home_team_id'] = ind
    games.loc[games.visit_team == team_name, 'visit_team_id'] = ind
    players.loc[players.team == team_name, 'team_id'] = ind
    
players.MIN = players.MIN.replace('NWT JUST SIGNED', None)
players.MIN = players.MIN.convert_objects(convert_numeric = True)

games.to_csv('games.csv',index = False)
players.to_csv('players.csv',index = False)