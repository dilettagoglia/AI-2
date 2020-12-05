import configparser

from data_structure.gameStatus import *
from connection.serverConnection import *
from connection.chatConnection import ConnectToChat
import re
from strategy.fuzzyStrategy import FuzzyControlSystem
from strategy.lowLevelStrategy import lowLevelStrategy
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

        # A Karen can play one game at a time. Game encapsulate all the information about the map and other players
        global game
        game = Game(None)
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

    def createGame(self, gameName, flags):
        """
        Create a new Game
        :param gameName: uniquely identifies the game.
        :return: True if created, False ow.
        """
        if flags is not None:
            response = self.serverSocket.send("NEW " + gameName + " "+flags)
        else:
            response = self.serverSocket.send("NEW " + gameName)
        if response[0] == "OK Created":
            game.name = gameName
            print(self.me.name + " created a game room: " + gameName)
            return True
        else:
            print(response)
            return False

    def leaveGame(self, reason=None):
        """
        Let the AI leave a game room (works only if game started).
        :param reason: specify the reason why the AI leaved the game.
        :return: True if leaved, False ow.
        """
        # currently doesn't work [ERROR 404 Game not found]

        if game.name is None:
            print("You are not in any game at the moment.")
            return False
        if reason is None:
            response = self.serverSocket.send(game.name + "LEAVE")
        else:
            response = self.serverSocket.send(game.name + "LEAVE" + " " + reason)
        if response[0] == "OK":
            print(self.me.name + " leaved the game " + game.name)
            game.name = None
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
        game.name = gameName
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

            self.chatSocket.connectToChannel(game.name)
            return True

        else:
            game.name = None
            print(self.me.name + ": " + response[0])
            return False

    def startGame(self):
        """
        Send Start command to the server. Only the AI who create the room can start the game.
        :return: True if the game started, False ow.
        """
        self.lookStatus()
        response = self.serverSocket.send(game.name + " START")

        if response[0] == 'OK Game started':
            print(game.name + " started.")

            return self.waitToStart()
        else:
            print(game.name + " " + response[0])
            return False

    def lookStatus(self):
        """
        Retrieve information about the game status and of all the player (allies and enemies) in that room.
        :return: True if information updated, False ow.
        """
        response = self.serverSocket.send(game.name + " STATUS")
        if response[0] == 'OK LONG':
            for s in range(0, len(response)):
                # Parse information about the Game
                if response[s].startswith("GA:"):
                    row = re.split(' |=', response[s])
                    game.name = row[2]
                    game.state = row[4]
                    game.size = row[6]

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
                        if game.allies.get(row[2]) is None and game.enemies.get(row[2]) is None:
                            pl = Player(row[4])
                            pl.symbol = row[2]
                            pl.team = row[6]
                            pl.x = int(row[8])
                            pl.y = int(row[10])
                            pl.state = row[12]
                            if pl.team == self.me.team:
                                game.allies[pl.symbol] = pl
                            else:
                                game.enemies[pl.symbol] = pl

                        elif game.allies.get(row[2]) is not None:
                            game.allies.get(row[2]).x = int(row[8])
                            game.allies.get(row[2]).y = int(row[10])
                            game.allies.get(row[2]).state = row[12]


                        elif game.enemies.get(row[2]) is not None:
                            game.enemies.get(row[2]).x = int(row[8])
                            game.enemies.get(row[2]).y = int(row[10])
                            game.enemies.get(row[2]).state = row[12]

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
        response = self.serverSocket.send(game.name + " LOOK")

        if response[0] == 'OK LONG':
            response.pop(0)
            response.pop(len(response) - 1)
            actualMap = []

            for i in range(0, len(response)):

                splitted = split(response[i])
                for j in range(0, len(splitted)):
                    # For each symbol in the map, check if it identifies a player. If so, update its position information
                    if game.allies.get(splitted[j]) is not None:
                        game.allies.get(splitted[j]).x = j
                        game.allies.get(splitted[j]).y = i

                    elif game.enemies.get(splitted[j]) is not None:
                        game.enemies.get(splitted[j]).x = j
                        game.enemies.get(splitted[j]).y = i
                    elif self.me.symbol == splitted[j]:
                        self.me.x = j
                        self.me.y = i

                    # Used only the first time that Karen looks at the map. Find FLAGS position
                    elif firstTime is True:

                        if splitted[j] == "x" and self.me.symbol.isupper():
                            game.wantedFlagName = "x"
                            game.wantedFlagX = j
                            game.wantedFlagY = i
                        elif splitted[j] == "x" and self.me.symbol.islower():
                            game.toBeDefendedFlagName = "x"
                            game.toBeDefendedFlagX = j
                            game.toBeDefendedFlagY = i
                        elif splitted[j] == "X" and self.me.symbol.islower():
                            game.wantedFlagName = "X"
                            game.wantedFlagX = j
                            game.wantedFlagY = i
                        elif splitted[j] == "X" and self.me.symbol.isupper():
                            game.toBeDefendedFlagName = "X"
                            game.toBeDefendedFlagX = j
                            game.toBeDefendedFlagY = i

                actualMap.append(splitted)

                if firstTime is True:
                    game.mapWidth = len(actualMap[0])
                    game.mapHeight = len(actualMap)


            return actualMap

        else:
            return None

    def nop(self):
        """
        Send a NOP command. (keep alive control)
        :return:
        """
        return self.serverSocket.send(game.name + " NOP")

    def move(self, direction):
        """
         Basic function that send the "MOOVE" command to the server
         :param direction: define where the AI wants to move.
         :return: 'OK moved', 'Ok blocked' or 'ERROR'
         """
        if direction is None:
            return False
        response = self.serverSocket.send(game.name + " MOVE " + direction)
        if response[0] is "OK Moved":
            return True
        return False

    def shoot(self, direction):
        """
        Basic function that send the "SHOOT" command to the server
        :param direction: define where the AI wants to shoot.
        :return: 'OK x' where x is the position where the bullet landed
        """
        return self.serverSocket.send(game.name + " SHOOT " + direction)

    def waitToStart(self):
        """
        Wait until the game start.
        :return: start strategy if started. False on ERROR.
        """
        self.lookStatus()
        while game.state == "LOBBY":
            self.lookStatus()

        if game.state == "ACTIVE":
            self.strategy(self.strategyType)
        else:
            print("Error. Game status from LOBBY to " + str(game.state))
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

    def llStrategy(self):
        """
        Call the lowLevelStrategy. Run to the flag with only basic forecasting decisions *PROTO1*
        :return: True at the end of the game
        """
        self.lookStatus()

        game.serverMap = self.lookAtMap(True)
        game.weightedMap = deterministicMap(self)

        while game.state != 'FINISHED' and self.me.state != "KILLED":

            nextActions = lowLevelStrategy(self, game.wantedFlagX, game.wantedFlagY)

            for (action, direction) in nextActions:
                if action == "move":
                    self.move(direction)
                if action == "shoot":
                    self.shoot(direction)

            # AGGIORNAMENTO
            game.serverMap = self.lookAtMap(False)
            game.weightedMap = deterministicMap(self)
            self.lookStatus()

        if game.state != "FINISHED":
            print(self.me.name + " è morto.")

        while game.state == "ACTIVE":
            self.lookStatus()

        return True

    def fStrategy(self):
        """
        Call the fuzzyStrategy. Uses fuzzy rule to take the best decision *PROTO2*
        :return:
        """
        self.lookStatus()

        game.serverMap = self.lookAtMap(True)
        game.weightedMap = deterministicMap(self)

        while game.state != 'FINISHED' and self.me.state != "KILLED":

            # if game.stage == 0:
            # endx, endy, nearestEnemyDistance = FuzzyControlSystemFirstStage(self.me, game, self.maxWeight)
            # elif game.stage == 1:
            # endx, endy, nearestEnemyDistance = FuzzyControlSystemSecondStage(self.me, game, self.maxWeight)
            # else:
            endx, endy, nearestEnemyDistance = FuzzyControlSystem(self.me, self.maxWeight)

            # Avoid useless LOOK if I can't die moving
            if int(nearestEnemyDistance // 2) > 2:
                for i in range(1, int(nearestEnemyDistance // 2)):

                    try:
                        direction, coordinates = self.me.movement.move(game.weightedMap, self.me, endx, endy)
                        if direction is not None:
                            if self.move(direction):
                                self.me.x = coordinates[0]
                                self.me.y = coordinates[1]
                    except():
                        print("Exception generated by movement.move")
            else:
                nextActions = lowLevelStrategy(self, endx, endy)

                for (action, direction) in nextActions:
                    if action == "move":
                        self.move(direction)
                    if action == "shoot":
                        self.shoot(direction)

            # AGGIORNAMENTO
            game.serverMap = self.lookAtMap(False)
            game.weightedMap = deterministicMap(self)
            # self.lookStatus()

        if game.state != "FINISHED":
            print(self.me.name + " è morto.")

        while game.state == "ACTIVE":
            self.lookStatus()

        return True
