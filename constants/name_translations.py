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
    'East Carolina': '[ECU](#f/eastcarolina)',
    'Florida Atlantic': '[FAU](#f/fau)',
    'Hawaii': "[Hawai'i](#f/hawaii)",
    'Louisiana Monroe': "[ULM](#f/ulm)",
    'Massachusetts': "[UMass](#f/umass)",
    'Miami (OH)': "[Miami (OH)](#f/miamioh)",
    'South Florida': "[USF](#f/usf)",
    'Texas A&M': "[Texas A&M](#f/texasam)",
    'Western Kentucky': "[WKY](#f/wku)"
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
