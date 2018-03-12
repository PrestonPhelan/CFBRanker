class BracketTeam:

    def __init__(self, attributes):
        # set instance values
        self.name = attributes['name']
        self.rating = attributes['rating']
        self.std_dev = attributes['std_dev']
        self.probabilities = [None for i in range(7)]

    def __str__(self):
        return "%s -- Rating: %s, Std_Dev: %s" % (
            self.name, self.rating, self.std_dev
        )
