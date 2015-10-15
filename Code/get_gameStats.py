#!/usr/bin/env python
#Author: Dimitry Slavin
#Name: "get_gameStats.py"
#Date Created: March 2015 (Estimated)
#Notes: None
#General Purpose: Calculate advanced statistics from basic statistics.  
#Detailed Purpose (Enumerated): None


import numpy as np
import pandas as pd

teams = pd.read_csv('teams_and_prefixes.csv')
games = pd.read_csv('games.csv',index_col = False, parse_dates = [1])
players = pd.read_csv('players.csv', index_col = False)

#Formatting the games data frame:
games.index = games['game_id']

#Cleanup:
games_to_throw_out = set(games.game_id) - set(players.game_id)
criterion = games.game_id.map(lambda x: x in games_to_throw_out)
games = games[~criterion]
#--------------------------------------#

#Stats to put in final data frame:
stats_existing1 = ['date','season', 'team','team_id','home_01','win_01','PTSF','PTSA']
stats_existing2 = ['AST', 'BLK', 'DREB', 'OREB', 'REB', 'MIN', 'PF', 'STL', 'TO', '3PM', '3PA', 'FGM', 'FGA', 'FTM', 'FTA', '+/-']
stats_calc = ['PTS_diff', 'PACE', 'AST_ratio','DEF_eff','OFF_eff','FGP_adj','TO_rate','DREB_p','OREB_p','FT_rate']

#Setting up the structure of the data frame and initializing:
game_ids = players.game_id.unique()
team_type = ['home', 'away']
iterables = [game_ids, team_type]
names = ['game_id', 'h_or_a']
index = pd.MultiIndex.from_product(iterables, names = names) 
gameStats = pd.DataFrame(index = index, columns = stats_existing1 + stats_existing2 + stats_calc)


test = games
test_players = players
#Creating a smaller, test data set to test code:
#criterion = players.game_id.map(lambda x: x in test.index.values.tolist())
#test_players = players[criterion]

for ind in test_players.game_id.unique().tolist():
	try:
	    TID = [test.loc[ind,'home_team_id'], test.loc[ind,'visit_team_id']]
	    PTS = [test.loc[ind,'home_team_score'], test.loc[ind,'visit_team_score']]
	    PTS_diff = PTS[0] - PTS[1]
	    
	    #home team stuff:  
	    gameStats.loc[(ind,'home'),['date','season','team','team_id']] = test.loc[ind,['date','season','home_team','home_team_id']].values
	    gameStats.loc[(ind,'home'),['home_01']] = True
	    if PTS_diff > 0:
	        gameStats.loc[(ind,'home'),['win_01']] = True
	        gameStats.loc[(ind,'away'),['win_01']] = False
	    else:
	        gameStats.loc[(ind,'home'),['win_01']] = False
	        gameStats.loc[(ind,'away'),['win_01']] = True
	        
	    gameStats.loc[(ind,'home'),['PTSF', 'PTSA']] = [PTS[0],PTS[1]]
	    gameStats.loc[(ind,'home'),['PTS_diff']] = PTS_diff
	    stats_home = test_players[test_players['team_id'] == TID[0]].groupby('game_id').sum().loc[ind,stats_existing2]
	    gameStats.loc[(ind,'home'),stats_existing2] = stats_home.values
	    
	    #away team stuff:
	    gameStats.loc[(ind,'away'),['date','season','team','team_id']] = test.loc[ind,['date','season','visit_team','visit_team_id']].values
	    gameStats.loc[(ind,'away'),['home_01']] = False
	    gameStats.loc[(ind,'away'),['PTSF', 'PTSA']] = [PTS[1],PTS[0]]
	    gameStats.loc[(ind,'away'),['PTS_diff']] = -PTS_diff

	    stats_away = test_players[test_players['team_id'] == TID[1]].groupby('game_id').sum().loc[ind,stats_existing2]
	    gameStats.loc[(ind,'away'),stats_existing2] = stats_away.values  

	    #assignment and calculation for stats_calc
	    AST = [stats_home.AST, stats_away.AST]
	    FGA = [stats_home.FGA, stats_away.FGA]
	    FGM = [stats_home.FGM, stats_away.FGM]
	    FTA = [stats_home.FTA, stats_away.FTA]
	    FTM = [stats_home.FTM, stats_away.FTM]
	    OREB = [stats_home.OREB, stats_away.OREB]
	    DREB = [stats_home.DREB, stats_away.DREB]
	    TO = [stats_home.TO, stats_away.TO]
	    threePM = [stats_home['3PM'], stats_away['3PM']]
	    
	    #home team assignments:
	    h = 0
	    a = 1
	    POSS = float(np.prod([0.5, ( (FGA[h] + np.prod([0.4,FTA[h]]) - np.prod([1.07, (OREB[h] / (OREB[h] + DREB[a])), (FGA[h] - FGM[h])]) + TO[h]) 
	                                   + (FGA[a] + np.prod([0.4,FTA[a]]) - np.prod([1.07, (OREB[a] / (OREB[a] + DREB[h])), (FGA[a] - FGM[a])]) + TO[a]))]))
	    gameStats.loc[(ind,'home'),['PACE']] = POSS
	    gameStats.loc[(ind,'home'),['AST_ratio']]= float((AST[h]*100) / (FGA[h]+(FTA[h]*0.44)+AST[h]+TO[h]))
	    gameStats.loc[(ind,'home'),['DEF_eff']] = 100*(PTS[a])/(POSS)
	    gameStats.loc[(ind,'home'),['OFF_eff']] = 100*(PTS[h])/(POSS)
	    gameStats.loc[(ind,'home'),['FGP_adj']] = float((FGM[h] + 0.5*(threePM[h]))/(FGA[h])) #SHOOTING (40%)
	    gameStats.loc[(ind,'home'),['TO_rate']] = float(TO[h]/POSS) #TURNOVERS (25%)
	    gameStats.loc[(ind,'home'),['DREB_p']] = float((DREB[h])/(DREB[h]+OREB[a])) #REBOUNDING (20%)
	    gameStats.loc[(ind,'home'),['OREB_p']] = float((OREB[h])/(OREB[h]+DREB[h]))
	    gameStats.loc[(ind,'home'),['FT_rate']] = float(FTM[h]/FGA[h]) #FREE THROW RATE (15%)
	    
	    #away team assignments:
	    h = 1
	    a = 0
	    gameStats.loc[(ind,'away'),['PACE']] = POSS
	    gameStats.loc[(ind,'away'),['AST_ratio']]= float((AST[h]*100) / (FGA[h]+(FTA[h]*0.44)+AST[h]+TO[h]))
	    gameStats.loc[(ind,'away'),['DEF_eff']] = 100*(PTS[a])/(POSS)
	    gameStats.loc[(ind,'away'),['OFF_eff']] = 100*(PTS[h])/(POSS)
	    gameStats.loc[(ind,'away'),['FGP_adj']] = float((FGM[h] + 0.5*(threePM[h]))/(FGA[h]))
	    gameStats.loc[(ind,'away'),['TO_rate']] = float(TO[h]/POSS)
	    gameStats.loc[(ind,'away'),['DREB_p']] = float((DREB[h])/(DREB[h]+OREB[a]))
	    gameStats.loc[(ind,'away'),['OREB_p']] = float((OREB[h])/(OREB[h]+DREB[h]))
	    gameStats.loc[(ind,'away'),['FT_rate']] = float(FTM[h]/FGA[h])
	except Exception as e:
	    print "Error in ", ind
	    print e

gameStats.to_csv('gameStats_2.csv')
    
