import numpy as np
import pandas as pd

teams = pd.read_csv('teams.csv')
games = pd.read_csv('games.csv')
players = pd.read_csv('players.csv')

games['date'] = pd.to_datetime(games['date'], format='%Y-%m-%d')

#FOR HOME TEAM IMPUTATION:
df = games
master_list = teams.team
df.home_team = df.home_team.replace('NY Knicks','New York Knicks')
for master_name in master_list:
    if (master_name != 'Los Angeles Clippers') and (master_name != 'Los Angeles Lakers'):
        for index, row in df.iterrows():
            if row.home_team in master_name:
                df.ix[index, 'home_team'] = master_name
            else:
                pass
    else:
        pass
    
df.loc[(df.home_team == 'Los Angeles') & (df.visit_team == 'Los Angeles Clippers'), 'home_team'] = 'Los Angeles Lakers'
df.loc[(df.home_team == 'Los Angeles') & (df.visit_team == 'Los Angeles Lakers'), 'home_team'] = 'Los Angeles Clippers'

still_missing = df.loc[df.home_team == 'Los Angeles',:].index
for ind in still_missing:
    match_date = df.date[ind]
    ids = df.loc[df.date < match_date, 'match_id'].values
    clippers_players = set(players.loc[players.match_id.isin(ids),:].groupby('team').get_group('Los Angeles Clippers').player_id)
    lakers_players = set(players.loc[players.match_id.isin(ids),:].groupby('team').get_group('Los Angeles Lakers').player_id)
    clip_players_NOLAK = clippers_players - lakers_players
    lak_players_NOCLIP = lakers_players - clippers_players
    
    for pid in clip_players_NOLAK:
        df.loc[(((df.hi_asts_pid == pid) | (df.hi_points_pid == pid) | (df.hi_rebs_pid == pid))
               & (df.home_team == 'Los Angeles')), 'home_team'] = 'Los Angeles Clippers'
    
    for pid in lak_players_NOCLIP:
        df.loc[(((df.hi_asts_pid == pid) | (df.hi_points_pid == pid) | (df.hi_rebs_pid == pid))
               & (df.home_team == 'Los Angeles')), 'home_team'] = 'Los Angeles Lakers'
        
#IMPUTING MISSING VALUES:
df.ix[9895,'home_team'] = 'Los Angeles Clippers'
df.loc[df.home_team == 'Los Angeles','home_team'] = 'Los Angeles Lakers' #the rest were lakers

#FOR VISIT TEAM IMPUTATION:
#FOR VISIT TEAM IMPUTATION:
df.visit_team = df.visit_team.replace('NY Knicks','New York Knicks')
for master_name in master_list:
    if (master_name != 'Los Angeles Clippers') and (master_name != 'Los Angeles Lakers'):
        for index, row in df.iterrows():
            if row.visit_team in master_name:
                df.ix[index, 'visit_team'] = master_name
            else:
                pass
    else:
        pass
    
df.loc[(df.visit_team == 'Los Angeles') & (df.home_team == 'Los Angeles Clippers'), 'visit_team'] = 'Los Angeles Lakers'
df.loc[(df.visit_team == 'Los Angeles') & (df.home_team == 'Los Angeles Lakers'), 'visit_team'] = 'Los Angeles Clippers'

still_missing = df.loc[df.visit_team == 'Los Angeles',:].index
for ind in still_missing:
    match_date = df.date[ind]
    ids = df.loc[df.date < match_date, 'match_id'].values
    clippers_players = set(players.loc[players.match_id.isin(ids),:].groupby('team').get_group('Los Angeles Clippers').player_id)
    lakers_players = set(players.loc[players.match_id.isin(ids),:].groupby('team').get_group('Los Angeles Lakers').player_id)
    clip_players_NOLAK = clippers_players - lakers_players
    lak_players_NOCLIP = lakers_players - clippers_players
    
    for pid in clip_players_NOLAK:
        df.loc[(((df.hi_asts_pid == pid) | (df.hi_points_pid == pid) | (df.hi_rebs_pid == pid))
               & (df.visit_team == 'Los Angeles')), 'visit_team'] = 'Los Angeles Clippers'
    
    for pid in lak_players_NOCLIP:
        df.loc[(((df.hi_asts_pid == pid) | (df.hi_points_pid == pid) | (df.hi_rebs_pid == pid))
               & (df.visit_team == 'Los Angeles')), 'visit_team'] = 'Los Angeles Lakers'
        
#IMPUTING MISSING VALUES:
clippers_inds = [151,6179,6552,7739,9917,9972,11142]
lakers_inds = [288, 2747,7691,11004,11175,12051,12359]
for ind in clippers_inds:
    df.ix[ind,'visit_team'] = 'Los Angeles Clippers'
for ind in lakers_inds:
    df.ix[ind,'visit_team'] = 'Los Angeles Lakers'

games = df
games = games.rename(columns={'match_id':'game_id'})
games = games.sort('game_id')
games.index = games['game_id']
games.to_csv('games.csv',index = False)
games.to_csv('games.csv', index = False)