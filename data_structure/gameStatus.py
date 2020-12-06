from data_structure.socialDedDB import *
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

        # in futuro per le strategy potremmo considerare eventuali variabili come :isInTheRiver (cosi so se puo spararmi) etc.


class Game:

    def __init__(self, gameName):
        self.name = gameName
        self.state = None
        # Valori possibili: 0, 1, 2 (fase 0 senza shoot, fase 1 no ctf, fase 2 gioco normale)
        self.stage = 0
        self.allies = dict()
        self.enemies = dict()

        self.mapHeight = None
        self.mapWidth = None

        self.toBeDefendedFlagX = None
        self.toBeDefendedFlagY = None
        self.toBeDefendedFlagName = None
        self.wantedFlagX = None
        self.wantedFlagY = None
        self.wantedFlagName = None
        self.serverMap = None
        self.weightedMap = None


global game
global mutex_ga
global db
global mutex_db
global sharedList
global mutex_sl

