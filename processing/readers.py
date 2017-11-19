def read_composite_line(line):
    elements = line.strip().split(',')
    mean, median, standard_deviation, rank, name = elements
    return { 'mean': float(mean), 'name': name }

def read_performance_line(line):
    elements = line.strip().split(',')
    strength_of_record, game_control, name = elements
    return {
        'strength_of_record': float(strength_of_record),
        'game_control': float(game_control),
        'name': name
        }

def process_power_name(name):
    result = name
    if name.endswith("St"):
        result = name + "ate"
    return result
