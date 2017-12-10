from models.team import Team

teams = Team.build_all_with_games('basketball')
# for team_id, team in teams.items():
#     print("%s %s %s" % (team_id, team, team.conference))
#
# print (len(teams.values()))
