import numpy as np
import pandas as pd

teams = pd.read_csv('teams.csv')
games = pd.read_csv('games.csv')
players = pd.read_csv('players.csv')

games.date = pd.to_datetime([date1.split(' ')[0] for date1 in games.date], format='%Y-%m-%d')

players.team = players.team.replace('Charlotte Bobcats', 'Charlotte Hornets')
players.team = players.team.replace('New Jersey Nets', 'Brooklyn Nets')
players.team = players.team.replace('No/oklahoma City Hornets', 'New Orleans Pelicans')
players.team = players.team.replace('New Orleans Hornets', 'New Orleans Pelicans')
players.team = players.team.replace('Seattle Supersonics', 'Oklahoma City Thunder')


players = players.sort('game_id')
players.to_csv('players.csv',index = False)