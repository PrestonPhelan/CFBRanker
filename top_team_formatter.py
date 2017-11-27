import os
root_path = os.path.dirname(os.path.abspath(__file__))

team_list = [
    'clemson',
    'oklahoma',
    'wisconsin',
    'auburn',
    'alabama',
    'georgia',
    'miami',
    'ohiostate',
    'usc',
    'ucf',
    'tcu',
    'pennstate'
    ]

team_lines = {}
for team in team_list:
    with open(root_path + '/output/reddit_schedules/%s.txt' % team) as f:
        team_lines[team] = list(f)
        if len(team_lines[team]) < 14:
            team_lines[team].append("| | | |\n")
    print(team_lines[team])

def write_combined_lines(file_obj, list_of_teams):
    lines1 = team_lines[list_of_teams[0]]
    lines2 = team_lines[list_of_teams[1]]
    lines3 = team_lines[list_of_teams[2]]
    for idx, _ in enumerate(lines1):
        if idx < 2:
            join_string = " | -- | "
        else:
            join_string = " -- | "
        line = join_string.join([lines1[idx].strip(), lines2[idx].strip(), lines3[idx].strip()])
        file_obj.write(line + '\n')

source = root_path + '/output/reddit-schedule-comparison.txt'
with open(source, 'w+') as f:
    write_combined_lines(f, team_list[:3])
    f.write('\n')
    write_combined_lines(f, team_list[3:6])
    f.write('\n')
    write_combined_lines(f, team_list[6:9])
    f.write('\n')
    write_combined_lines(f, team_list[9:])
