from ./team import Team

def build_teams(sourcefile):
    teams = {}
    source = open(sourcefile, "r")
    name_list = source.readlines()
    source.close()
    for line in name_list:
        name = line.strip()
        teams[name] = Team(name)
    return teams
