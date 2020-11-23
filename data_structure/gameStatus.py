class Player:

    def __init__(self, name):
        self.movement = None
        self.state = None
        self.name = name
        self.symbol = None
        self.team = None
        self.score = None
        self.energy = None
        self.loyalty = None
        self.x = None
        self.y = None

        #in futuro per le strategy potremmo considerare eventuali variabili come :isInTheRiver (cosi so se puo spararmi) etc.

class Game:

    def __init__(self, gameName):
        self.serverMap = None
        self.weightedMap = None
        self.name = gameName
        self.state = None
        self.allies = dict()
        self.enemies = dict()
        self.me = None
        self.toBeDefendedFlagX = None
        self.toBeDefendedFlagY = None
        self.toBeDefendedFlagName = None
        self.wantedFlagX = None
        self.wantedFlagY = None
        self.wantedFlagName = None