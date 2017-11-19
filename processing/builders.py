def build_conference_flairs(data):
    result = {}
    for line in data:
        abrev, flair = line.strip().split(',')
        result[abrev] = flair
    return result
