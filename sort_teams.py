lines = []
with open('./constants/unsorted_teams.csv', 'r') as f:
    for line in f:
        lines.append(line)

with open('./constants/teams.csv', 'w+') as f:
    for line in list(sorted(lines)):
        f.write(line)
