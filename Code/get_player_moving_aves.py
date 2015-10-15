#!/usr/bin/env python
#Author: Dimitry Slavin
#Name: "get_player_moving_aves.py"
#Date Created: March 2015 (Estimated)
#Notes: None
#General Purpose: Calculate moving averages of players statistics.  
#Detailed Purpose (Enumerated): None


import numpy as np
import pandas as pd

teams = pd.read_csv('teams.csv')
games = pd.read_csv('games.csv',index_col = False)
players = pd.read_csv('players.csv', index_col = False)

games.date = pd.to_datetime([date1.split(' ')[0] for date1 in games.date], format='%Y-%m-%d')

#-----------------------------------#

#Function that gets player stats for previous games
def get_past_player_stats(players, game_id, num_games_lookback, min_mins_played):
    pt_ids = players.loc[(players.match_id == game_id), ['player_id','team_id']]
    pt_ids.index = pt_ids.player_id
    player_stats = pd.DataFrame(columns = [u'match_id',u'player_id',u'AST', u'BLK', u'DREB', 
                                           u'OREB', u'PF', u'+/-', u'PTS', 
                                           u'REB', u'STL', u'TO', u'3PM', u'3PA', 
                                           u'FGM', u'FGA', u'FTM', u'FTA'])
    groupedDF = players.groupby(players.player_id)
    for pid in pt_ids.player_id:
        foo = groupedDF.get_group(pid)
        foo = foo.loc[(foo.match_id < game_id) &
                                         (foo.MIN >= min_mins_played),player_stats.columns]
        foo = foo.sort('match_id').tail(num_games_lookback)
        player_stats = player_stats.append(foo)
    player_stats = player_stats.groupby(player_stats.player_id).mean()
    player_stats = player_stats.join(pt_ids.team_id)
    return player_stats

#Function that gets past game stats
def get_past_game_stats(games, game_id, num_games_lookback, team_id1 = None, team_id2 = None):
    game_stats = games.loc[games.match_id == game_id,:] #stats for current game
    home_team = int(game_stats.home_team_id.values)
    visit_team = int(game_stats.visit_team_id.values)
    
    if ((team_id1 == None) & (team_id2 == None)):
        home_team_stats = games.loc[(games.match_id < game_id) &
                                    ((games.home_team_id == home_team) | (games.visit_team_id == home_team)),:]
        home_team_stats = home_team_stats.sort('match_id').tail(num_games_lookback)
        
        visit_team_stats = games.loc[(games.match_id < game_id) &
                                     ((games.home_team_id == visit_team) | (games.visit_team_id == visit_team)),:]
        visit_team_stats = visit_team_stats.sort('match_id').tail(num_games_lookback)
        return home_team_stats.append(visit_team_stats)
    
    elif ((team_id1 == home_team) & (team_id2 == None)):
        home_team_stats = games.loc[(games.match_id < game_id) &
                                    ((games.home_team_id == home_team) | (games.visit_team_id == home_team)),:]
        return home_team_stats.sort('match_id').tail(num_games_lookback)
    
    elif ((team_id1 == visit_team) & (team_id2 == None)):
        visit_team_stats = games.loc[(games.match_id < game_id) &
                                     ((games.home_team_id == visit_team) | (games.visit_team_id == visit_team)),:]
        return visit_team_stats.sort('match_id').tail(num_games_lookback)
    
    elif (set([team_id1,team_id2]) == set([home_team,visit_team])):
        matchup_stats = games.loc[(games.match_id < game_id) & 
                         (((games.home_team_id == home_team) & (games.visit_team_id == visit_team)) |
                          ((games.home_team_id == visit_team) & (games.visit_team_id == home_team))),:]
        return matchup_stats.sort('match_id').tail(num_games_lookback)
    
    else:
        return "Something went wrong. Check team_id argument."

#Code to generate moving average predictors:
final_stats = pd.DataFrame()
for game_id in games.loc[games.season == 2014, 'match_id'].values:
    try:
        num_games_lookback = 5
        min_mins_played = 1

        team_stats1 = get_past_player_stats(players,game_id, num_games_lookback, min_mins_played).groupby('team_id').sum()
        team_stats1 = team_stats1.loc[:,'AST'::]
        team_stats1['3PP'] = team_stats1['3PM']/team_stats1['3PA']
        team_stats1['FGP'] = team_stats1['FGM']/team_stats1['FGA']
        team_stats1['FTP'] = team_stats1['FTM']/team_stats1['FTA']

        game_stats = games.loc[games.match_id == game_id, :]
        home_team_id = int(game_stats.home_team_id.values)
        visit_team_id = int(game_stats.visit_team_id.values)
        win_team_id = int(game_stats.win_team_id.values)
        lose_team_id = int(game_stats.lose_team_id.values)

        team_stats1.reindex([home_team_id, visit_team_id])
        past_stats = get_past_game_stats(games, game_id, num_games_lookback)
        home_num_wins = past_stats.loc[past_stats.win_team_id == home_team_id,'win_team_id'].count()
        visit_num_wins = past_stats.loc[past_stats.win_team_id == visit_team_id,'win_team_id'].count()
        num_wins = pd.DataFrame([home_num_wins,visit_num_wins], index = [home_team_id, visit_team_id])
        team_stats1['num_wins'] = num_wins

        stat_diff = team_stats1.loc[win_team_id] - team_stats1.loc[lose_team_id]
        final_stats = final_stats.append(stat_diff, ignore_index = True)
    except Exception as e:
        print "Error in ", game_id

final_stats = final_stats.loc[:,['3PP','AST','BLK','DREB','FGP','FTP','OREB','PF','PTS','STL','TO','num_wins']]
for ind,row in final_stats.iterrows():
    final_stats = final_stats.append(-1*row)
final_stats.loc[final_stats.win == -1, 'win'] = 0

final_stats.to_csv('stats2014.csv')