from models.team import Team

teams = Team.build_all(football=True)
for team_id, team in teams.items():
    print("%s %s %s" % (team_id, team, team.conference))

print (len(teams.values()))
