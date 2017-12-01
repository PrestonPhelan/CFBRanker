# With Power, Use Pattern to turn St at end into State
POWER_NAMES = {
 'Miami FL': 'Miami',
 'FL Atlantic': 'Florida Atlantic',
 'N Illinois': 'Northern Illinois',
 'Mississippi': 'Ole Miss',
 'W Michigan': 'Western Michigan',
 'C Michigan': 'Central Michigan',
 'E Michigan': 'Eastern Michigan',
 'Florida Intl': 'FIU',
 'MTSU': 'Middle Tennessee',
 'Miami OH': 'Miami (OH)',
 'WKU': 'Western Kentucky',
 'ULM': 'Louisiana Monroe',
 'ULL': 'Louisiana',
 'Kent': 'Kent State',
 'Coastal Car': 'Coastal Carolina',
 'Ga Southern': 'Georgia Southern',
 'UT San Antonio': 'UTSA'
}

PERFORMANCE_NAMES = {
 'Florida Intl Golden Panthers': 'FIU',
 "Hawai'i Rainbow Warriors": "Hawaii",
 "Southern Mississippi Golden Eagles": "Southern Miss",
 "UT San Antonio Roadrunners": "UTSA",
 "UMass Minutemen": "Massachusetts"
}

NCAA_NAMES = {
    'Louisiana-Monroe': 'Louisiana Monroe',
    'Louisiana-Lafayette': 'Louisiana',
    'Miami (FL)': 'Miami',
    'Southern Methodist': 'SMU',
    'Brigham Young': 'BYU',
    'North Carolina State': 'NC State',
    'Florida International': 'FIU'
}

REDDIT_NAMES = {
    # Unlike others above, this dictionary has keys that
    # are the standard names, and translates for output
    # in reddit flairs
    'East Carolina': '[ECU](#f/eastcarolina) East Carolina',
    'Florida Atlantic': '[FAU](#f/fau) Florida Atlantic',
    'Hawaii': "[Hawai'i](#f/hawaii) Hawaii",
    'Louisiana Monroe': "[ULM](#f/ulm) Louisiana-Monroe",
    'Massachusetts': "[UMass](#f/umass) Massachusetts",
    'Miami (OH)': "[Miami (OH)](#f/miamioh) Miami(OH)",
    'South Florida': "[USF](#f/usf) South Florida",
    'Texas A&M': "[Texas A&M](#f/texasam) Texas A&M",
    'Western Kentucky': "[WKU](#f/wku) Western Kentucky"
}

SCHEDULE_NAMES = {
    'Southern Mississippi': 'Southern Miss',
    'UT San Antonio': 'UTSA',
    'UMass': 'Massachusetts',
    "Hawai'i": 'Hawaii',
    'Florida Intl': 'FIU'
}

def find_match(name, dictionary):
    """For use with PERFORMANCE_NAMES."""
    if name == '':
        raise "Didn't find name"
    search_name = (' ').join(name.split(' ')[:-1])
    if search_name in dictionary:
        return search_name
    else:
        return find_match(search_name, dictionary)

def generic_translation(name, dictionary):
    if name in dictionary:
        return dictionary[name]
    else:
        return name

def translate_ncaa_name(name):
    return generic_translation(name, NCAA_NAMES)

def translate_schedule_name(name):
    return generic_translation(name, SCHEDULE_NAMES)
