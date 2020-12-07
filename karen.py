import configparser
from data_structure import gameStatus
from data_structure.gameStatus import *
from connection.serverConnection import *
from connection.chatConnection import ConnectToChat, ReceiveThread
import re

from social_deduction.chatAnalyzer import *
from strategy.fuzzyStrategy import FuzzyControlSystem, FuzzyControlSystemImpostor
from strategy.lowLevelStrategy import lowLevelStrategy, lowLevelStrategyImpostor
from strategy.deterministicMap import deterministicMap
from strategy.movement import *


class Karen:
    """
    Karen identify the AI-subsystem that is able to play an AmongAIs match
    """

    def __init__(self, name, strategyType):
        """
        Construct a new 'Karen' object.

        :param name: The name of the AI
        :return: returns nothing
        """
        # Identify the Karen as a Player
        self.me = Player(name)

        gameStatus.game = Game(None)
        gameStatus.db = DecisionsDB()
        gameStatus.sharedList = []

        self.me.movement = rb_movement(movement)
        self.strategyType = strategyType

        config = configparser.ConfigParser()
        config.read('config')

        self.host = config['connectionParam']['HOST']
        self.port = config['connectionParam']['PORT']
        self.delay = config['connectionParam']['DELAY']

        self.host_chat = config['chatParam']['HOST']
        self.port_chat = config['chatParam']['PORT']

        self.maxWeight = int(config['envParam']["MAXWEIGHT"])

        # Initialize the connection to the server and the chat system
        self.serverSocket = connectToServer(self.host, self.port, self.delay)

        self.ChatHOST = config['chatParam']['HOST']
        self.ChatPORT = config['chatParam']['PORT']

        self.chatSocket = ConnectToChat(self.ChatHOST, self.ChatPORT, self.me.name)
        t_r = ReceiveThread('Receive', self.chatSocket.net, self.me.name)
        t_r.start()


    def createGame(self, gameName, flags):
        """
        Create a new Game
        :param flags: T training, Q squared, W wide, 123 map dimension
        :param gameName: uniquely identifies the gameStatus.game.
        :return: True if created, False ow.
        """
        print('Creo game')
        # A Karen can play one game at a time. Game encapsulate all the information about the map and other players
        if flags is not None:
            response = self.serverSocket.send("NEW " + gameName + " " +flags)
        else:
            response = self.serverSocket.send("NEW " + gameName)

        if response[0] == "OK Created":
            gameStatus.game.name = gameName
            print(self.me.name + " created a game room: " + gameName)
            return True
        else:
            print(response)
            return False

    def leaveGame(self, reason=None):
        """
        Let the AI leave a game room (works only if game started).
        :param reason: specify the reason why the AI leaved the gameStatus.game.
        :return: True if leaved, False ow.
        """
        # currently doesn't work [ERROR 404 Game not found]

        if gameStatus.game.name is None:
            print("You are not in any game at the moment.")
            return False
        if reason is None:
            response = self.serverSocket.send(gameStatus.game.name + "LEAVE")
        else:
            response = self.serverSocket.send(gameStatus.game.name + "LEAVE" + " " + reason)
        if response[0] == "OK":
            print(self.me.name + " leaved the game " + gameStatus.game.name)
            gameStatus.game.name = None
            return True
        else:
            print(self.me.name + ": " + response[0])
            return False

    def joinGame(self, gameName, nature, role, userInfo=None):
        """
        Let the AI join a game
        :param gameName: specify which game the AI want to join.
        :param nature: specify that the player is the AI.
        :param role: specify the role of the AI. (normal player, impostor and so on)
        :param userInfo: extra user info.
        :return: True if joined, False ow.
        """
        # <game> JOIN <player-name> <nature> <role> <user-info>
        gameStatus.game.name = gameName
        self.me.nature = nature
        self.me.role = role
        self.me.userInfo = userInfo
        cmd = gameName + " JOIN " + self.me.name + " " + nature + " " + role
        if userInfo is not None:
            cmd += " " + userInfo

        response = self.serverSocket.send(cmd)

        if response[0].startswith("OK"):
            row = re.split(' |=', response[0])
            self.me.team = row[2]
            self.me.loyalty = row[4]

            self.chatSocket.connectToChannel(gameStatus.game.name)
            return True

        else:
            gameStatus.game.name = None
            print(self.me.name + ": " + response[0])
            return False

    def startGame(self):
        """
        Send Start command to the server. Only the AI who create the room can start the gameStatus.game.
        :return: True if the game started, False ow.
        """
        self.lookStatus()

        pl = SD_Player(self.me.name, self.me.team)
        gameStatus.db.playerList[self.me.name] = pl
        threadino = ChatAnalysisThread(self.me.name)
        threadino.start()
        SD_thread = SocialDeductionThread()
        SD_thread.start()

        response = self.serverSocket.send(gameStatus.game.name + " START")

        if response[0] == 'OK Game started':
            print(gameStatus.game.name + " started.")

            return self.waitToStart()
        else:
            print(gameStatus.game.name + " " + response[0])
            return False

    def lookStatus(self):
        """
        Retrieve information about the game status and of all the player (allies and enemies) in that room.
        :return: True if information updated, False ow.
        """
        response = self.serverSocket.send(gameStatus.game.name + " STATUS")

        if response[0] == 'OK LONG':
            for s in range(0, len(response)):
                # Parse information about the Game
                if response[s].startswith("GA:"):
                    row = re.split(' |=', response[s])
                    gameStatus.game.name = row[2]
                    gameStatus.game.state = row[4]
                    gameStatus.game.size = row[6]

                # Parse information about Karen
                if response[s].startswith("ME:"):
                    row = re.split(' |=', response[s])
                    self.me.symbol = row[2]
                    self.me.name = row[4]
                    self.me.team = row[6]
                    self.me.loyalty = row[8]
                    self.me.energy = row[10]
                    self.me.score = row[12]

                # Parse information about other players (allies or enemies)
                elif response[s].startswith("PL:"):
                    row = re.split(' |=', response[s])

                    # Karen is also present in the PLAYER list
                    if row[2] == self.me.symbol:
                        self.me.x = int(row[8])
                        self.me.y = int(row[10])
                        self.me.state = row[12]
                    # Not Karen, update information of other players

                    else:
                        if gameStatus.game.allies.get(row[2]) is None and gameStatus.game.enemies.get(row[2]) is None:
                            pl = Player(row[4])
                            pl.symbol = row[2]
                            pl.team = row[6]
                            pl.x = int(row[8])
                            pl.y = int(row[10])
                            pl.state = row[12]
                            if pl.team == self.me.team:
                                gameStatus.game.allies[pl.symbol] = pl
                            else:
                                gameStatus.game.enemies[pl.symbol] = pl

                        elif gameStatus.game.allies.get(row[2]) is not None:
                            gameStatus.game.allies.get(row[2]).x = int(row[8])
                            gameStatus.game.allies.get(row[2]).y = int(row[10])
                            gameStatus.game.allies.get(row[2]).state = row[12]


                        elif gameStatus.game.enemies.get(row[2]) is not None:
                            gameStatus.game.enemies.get(row[2]).x = int(row[8])
                            gameStatus.game.enemies.get(row[2]).y = int(row[10])
                            gameStatus.game.enemies.get(row[2]).state = row[12]
            return True

        else:
            return False

    def lookAtMap(self, firstTime):

        def split(word):
            return [char for char in word]

        """
        Let the AI to look at the map (works only if the game started).
        This function update all the information about the players in the 'Game' structure.
        :param firstTime: True if this is the first time the function is called. Used to retrieve FLAGS position.
        :return: The map if available, None ow.
        """
        response = self.serverSocket.send(gameStatus.game.name + " LOOK")

        if response[0] == 'OK LONG':
            response.pop(0)
            response.pop(len(response) - 1)
            actualMap = []

            for i in range(0, len(response)):

                splitted = split(response[i])
                for j in range(0, len(splitted)):
                    # For each symbol in the map, check if it identifies a player. If so, update its position information
                    if gameStatus.game.allies.get(splitted[j]) is not None:
                        gameStatus.game.allies.get(splitted[j]).x = j
                        gameStatus.game.allies.get(splitted[j]).y = i

                    elif gameStatus.game.enemies.get(splitted[j]) is not None:
                        gameStatus.game.enemies.get(splitted[j]).x = j
                        gameStatus.game.enemies.get(splitted[j]).y = i
                    elif self.me.symbol == splitted[j]:
                        self.me.x = j
                        self.me.y = i

                    # Used only the first time that Karen looks at the map. Find FLAGS position
                    elif firstTime is True:

                        if splitted[j] == "x" and self.me.symbol.isupper():
                            gameStatus.game.wantedFlagName = "x"
                            gameStatus.game.wantedFlagX = j
                            gameStatus.game.wantedFlagY = i
                        elif splitted[j] == "x" and self.me.symbol.islower():
                            gameStatus.game.toBeDefendedFlagName = "x"
                            gameStatus.game.toBeDefendedFlagX = j
                            gameStatus.game.toBeDefendedFlagY = i
                        elif splitted[j] == "X" and self.me.symbol.islower():
                            gameStatus.game.wantedFlagName = "X"
                            gameStatus.game.wantedFlagX = j
                            gameStatus.game.wantedFlagY = i
                        elif splitted[j] == "X" and self.me.symbol.isupper():
                            gameStatus.game.toBeDefendedFlagName = "X"
                            gameStatus.game.toBeDefendedFlagX = j
                            gameStatus.game.toBeDefendedFlagY = i

                actualMap.append(splitted)

                if firstTime is True:
                    gameStatus.game.mapWidth = len(actualMap[0])
                    gameStatus.game.mapHeight = len(actualMap)


            return actualMap

        else:
            return None

    def nop(self):
        """
        Send a NOP command. (keep alive control)
        :return:
        """
        return self.serverSocket.send(gameStatus.game.name + " NOP")

    def move(self, direction):
        """
         Basic function that send the "MOOVE" command to the server
         :param direction: define where the AI wants to move.
         :return: 'OK moved', 'Ok blocked' or 'ERROR'
         """
        if direction is None:
            return False
        response = self.serverSocket.send(gameStatus.game.name + " MOVE " + direction)
        if response[0] == "OK moved":
            return True
        return False

    def shoot(self, direction):
        """
        Basic function that send the "SHOOT" command to the server
        :param direction: define where the AI wants to shoot.
        :return: 'OK x' where x is the position where the bullet landed
        """
        return self.serverSocket.send(gameStatus.game.name + " SHOOT " + direction)

    def waitToStart(self):
        """
        Wait until the game start.
        :return: start strategy if started. False on ERROR.
        """
        self.lookStatus()
        while gameStatus.game.state == "LOBBY":
            self.lookStatus()

        if gameStatus.game.state == "ACTIVE":
            self.strategy(self.strategyType)
        else:
            print("Error. Game status from LOBBY to " + str(gameStatus.game.state))
            return False
        return True

    def strategy(self, strategyType):
        """
        Strategies Dispatcher
        :param strategyType: the type of the strategy. Defined in Karen's init
        :return: -
        """

        if strategyType == "lowLevelStrategy":
            self.llStrategy()

        if strategyType == "fuzzyStrategy":

            self.fStrategy()

        else:
            print("Hai sbagliato nome della strategy. Riprova controllando i param di Karen.")
            return False



    def llStrategy(self):
        """
        Call the lowLevelStrategy. Run to the flag with only basic forecasting decisions *PROTO1*
        :return: True at the end of the game
        """
        self.lookStatus()

        gameStatus.game.serverMap = self.lookAtMap(True)
        gameStatus.game.weightedMap = deterministicMap(self.me, self.maxWeight)

        while gameStatus.game.state != 'FINISHED' and self.me.state != "KILLED":

            nextActions = lowLevelStrategy(self, gameStatus.game.wantedFlagX, gameStatus.game.wantedFlagY)

            for (action, direction) in nextActions:
                if action == "move":
                    self.move(direction)
                if action == "shoot":
                    self.shoot(direction)

            # AGGIORNAMENTO
            gameStatus.game.serverMap = self.lookAtMap(False)
            gameStatus.game.weightedMap = deterministicMap(self.me, self.maxWeight)
            self.lookStatus()

        if gameStatus.game.state != "FINISHED":
            print(self.me.name + " è morto.")

        while gameStatus.game.state == "ACTIVE":
            self.lookStatus()

        return True

    def fStrategy(self):
        """
        Call the fuzzyStrategy. Uses fuzzy rule to take the best decision.
        This function will check if you are an impostor or not and check in which is the game's stage
        :return:
        """

        gameStatus.game.serverMap = self.lookAtMap(True)
        gameStatus.game.weightedMap = deterministicMap(self.me, self.maxWeight)

        while gameStatus.game.state != 'FINISHED' and self.me.state != "KILLED":
            # check the game stage and if i'm an impostor or not
            if self.me.loyalty == self.me.team:
                # if gameStatus.game.stage == 0:
                # endx, endy, nearestEnemyDistance = FuzzyControlSystemFirstStage(self.me, game, self.maxWeight)
                # elif gameStatus.game.stage == 1:
                # endx, endy, nearestEnemyDistance = FuzzyControlSystemSecondStage(self.me, game, self.maxWeight)
                # else:
                endx, endy, nearestEnemyDistance = FuzzyControlSystem(self.me, self.maxWeight)
            else:

                endx, endy, nearestEnemyDistance = FuzzyControlSystemImpostor(self.me, self.maxWeight)
                print(self.me.name + " impostor")
            # Avoid useless LOOK if I can't die moving
            if int(nearestEnemyDistance // 2) > 2:
                for i in range(1, int(nearestEnemyDistance // 2)):

                    try:
                        direction, coordinates = self.me.movement.move(gameStatus.game.weightedMap, self.me, endx, endy)
                        if direction is not None:
                            if self.move(direction):
                                self.me.x = coordinates[0]
                                self.me.y = coordinates[1]
                    except():
                        print("Exception generated by movement.move")
            else:
                if self.me.loyalty == self.me.team:

                    nextActions = lowLevelStrategy(self, endx, endy)
                else:
                    nextActions = lowLevelStrategyImpostor(self, endx, endy)
                    print(self.me.name + " impostor")

                for (action, direction) in nextActions:
                    if action == "move":
                        self.move(direction)
                    if action == "shoot":
                        self.shoot(direction)

            # AGGIORNAMENTO
            gameStatus.game.serverMap = self.lookAtMap(False)
            gameStatus.game.weightedMap = deterministicMap(self.me, self.maxWeight)

        if gameStatus.game.state != "FINISHED":
            print(self.me.name + " è morto.")

        while gameStatus.game.state == "ACTIVE":
            self.lookStatus()

        return True
