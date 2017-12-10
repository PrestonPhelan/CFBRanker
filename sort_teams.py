conferences = {}
with open('./constants/conferences.csv', 'r') as f:
    for line in f:
        conf_id, _, display_name, _, _, _ = line.strip().split(',')
        conferences[conf_id] = { 'name': display_name, 'fb_members': [], 'bb_members': [] }

with open('./constants/teams.csv', 'r') as f:
    for line in f:
        columns = line.strip().split(',')
        if columns[7] != "None":
            conferences[columns[7]]['fb_members'].append(columns[0])
        conferences[columns[8]]['bb_members'].append(columns[0])

for conf_id, data in conferences.items():
    print(data['name'])
    print("--------------------")
    for team in data['fb_members']:
        print(team)
    print("\n")
    print("********************")
    print("\n")

for conf_id, data in conferences.items():
    print(data['name'])
    print("--------------------")
    for team in data['bb_members']:
        print(team)
    print("\n")
    print("********************")
    print("\n")
