class Conference:
    def __init__(self, line):
        self.id, self.name, self.abbreviation, self.flair = line.strip().split(",")
