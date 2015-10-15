def get_team_stats(players, game_id, num_games_lookback, min_mins_played):
    pt_ids = players.loc[(players.match_id == game_id), ['player_id','team_id']]
    pt_ids.index = pt_ids.player_id
    player_stats = pd.DataFrame(columns = [u'player_id',u'AST', u'BLK', u'DREB', 
                                           u'MIN', u'OREB', u'PF', u'+/-', u'PTS', 
                                           u'REB', u'STL', u'TO', u'3PM', u'3PA', 
                                           u'FGM', u'FGA', u'FTM', u'FTA'])
    groupedDF = players.groupby(players.player_id)
    for pid in pt_ids.player_id:
        foo = groupedDF.get_group(pid)
        foo = foo.loc[(foo.match_id < game_id) &
                                         (foo.MIN >= min_mins_played),player_stats.columns].tail(num_games_lookback)
        player_stats = player_stats.append(foo)
    player_stats = player_stats.groupby(player_stats.player_id).mean()
    player_stats = player_stats.join(pt_ids.team_id)
    team_stats = player_stats.groupby('team_id').sum()
    return team_stats