import configparser
from data_structure import gameStatus
from data_structure.gameStatus import *
from connection.serverConnection import *
from connection.chatConnection import ConnectToChat, ReceiveThread
import re

from social_deduction.chatAnalyzer import *
from strategy.fuzzyStrategy import *
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
        gameStatus.game = Game(None)
        gameStatus.db = DecisionsDB()
        gameStatus.sharedList = []
        gameStatus.game.me = Player(name)

        gameStatus.game.me.movement = rb_movement(movement)
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

        self.chatSocket = ConnectToChat(self.ChatHOST, self.ChatPORT, gameStatus.game.me.name)
        t_r = ReceiveThread('Receive', self.chatSocket.net, gameStatus.game.me.name)
        t_r.start()

    def createGame(self, gameName, flags):
        time.sleep(0.5)

        """
        Create a new Game
        :param flags: T training, Q squared, W wide, 123 map dimension
        :param gameName: uniquely identifies the gameStatus.game.
        :return: True if created, False ow.
        """
        print('Creo game')
        # A Karen can play one game at a time. Game encapsulate all the information about the map and other players
        if flags is not None:
            response = self.serverSocket.send("NEW " + gameName + " " + flags)
        else:
            response = self.serverSocket.send("NEW " + gameName)

        if response[0] == "OK Created":
            gameStatus.game.name = gameName
            print(gameStatus.game.me.name + " created a game room: " + gameName)
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
            print(gameStatus.game.me.name + " leaved the game " + gameStatus.game.name)
            gameStatus.game.name = None
            return True
        else:
            print(gameStatus.game.me.name + ": " + response[0])
            return False

    def joinGame(self, gameName, nature, role, userInfo=None):
        time.sleep(0.6)
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
        gameStatus.game.me.nature = nature
        gameStatus.game.me.role = role
        gameStatus.game.me.userInfo = userInfo
        cmd = gameName + " JOIN " + gameStatus.game.me.name + " " + nature + " " + role
        if userInfo is not None:
            cmd += " " + userInfo

        response = self.serverSocket.send(cmd)

        if response[0].startswith("OK"):
            row = re.split(' |=', response[0])
            gameStatus.game.me.team = row[2]
            gameStatus.game.me.loyalty = row[4]

            self.chatSocket.connectToChannel(gameStatus.game.name)
            return True

        else:
            gameStatus.game.name = None
            print(gameStatus.game.me.name + ": " + response[0])
            return False

    def startGame(self):
        """
        Send Start command to the server. Only the AI who create the room can start the gameStatus.game.
        :return: True if the game started, False ow.
        """
        time.sleep(0.5)
        self.lookStatus()
        time.sleep(0.5)

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
                    gameStatus.game.me.symbol = row[2]
                    gameStatus.game.me.name = row[4]
                    gameStatus.game.me.team = row[6]
                    gameStatus.game.me.loyalty = row[8]
                    gameStatus.game.me.energy = row[10]
                    gameStatus.game.me.score = row[12]

                # Parse information about other players (allies or enemies)
                elif response[s].startswith("PL:"):
                    row = re.split(' |=', response[s])

                    # Karen is also present in the PLAYER list
                    if row[2] == gameStatus.game.me.symbol:
                        gameStatus.game.me.x = int(row[8])
                        gameStatus.game.me.y = int(row[10])
                        gameStatus.game.me.state = row[12]
                    # Not Karen, update information of other players

                    else:
                        if gameStatus.game.allies.get(row[2]) is None and gameStatus.game.enemies.get(row[2]) is None:
                            pl = Player(row[4])
                            pl.symbol = row[2]
                            pl.team = row[6]
                            pl.x = int(row[8])
                            pl.y = int(row[10])
                            pl.state = row[12]
                            if pl.team == gameStatus.game.me.team:
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
                    elif gameStatus.game.me.symbol == splitted[j]:
                        gameStatus.game.me.x = j
                        gameStatus.game.me.y = i

                    # Used only the first time that Karen looks at the map. Find FLAGS position
                    elif firstTime is True:

                        wallx = 0
                        wally = 0
                        if splitted[j] == "#":
                            wallx = j
                            wally = i
                            gameStatus.game.walls.append([wallx, wally])
                            # print('Muri :' + str(gameStatus.game.walls))

                        if splitted[j] == "x" and gameStatus.game.me.symbol.isupper():
                            gameStatus.game.wantedFlagName = "x"
                            gameStatus.game.wantedFlagX = j
                            gameStatus.game.wantedFlagY = i
                        elif splitted[j] == "x" and gameStatus.game.me.symbol.islower():
                            gameStatus.game.toBeDefendedFlagName = "x"
                            gameStatus.game.toBeDefendedFlagX = j
                            gameStatus.game.toBeDefendedFlagY = i
                        elif splitted[j] == "X" and gameStatus.game.me.symbol.islower():
                            gameStatus.game.wantedFlagName = "X"
                            gameStatus.game.wantedFlagX = j
                            gameStatus.game.wantedFlagY = i
                        elif splitted[j] == "X" and gameStatus.game.me.symbol.isupper():
                            gameStatus.game.toBeDefendedFlagName = "X"
                            gameStatus.game.toBeDefendedFlagX = j
                            gameStatus.game.toBeDefendedFlagY = i

                actualMap.append(splitted)

                if firstTime is True:
                    gameStatus.game.mapWidth = len(actualMap[0])
                    gameStatus.game.mapHeight = len(actualMap)

            return actualMap

        else:
            print("Map not retrieved.")
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
            # print('Ok moved')
            return True
        return False

    def shoot(self, direction):
        """
        Basic function that send the "SHOOT" command to the server
        :param direction: define where the AI wants to shoot.
        :return: 'OK x' where x is the position where the bullet landed
        """
        return self.serverSocket.send(gameStatus.game.name + " SHOOT " + direction)

    def accuse(self, playerName):
        """
         Basic function that send the "ACCUSE" command to the server
         :param: 'playerName', name of the player that I want to vote
         :return: 'OK noted', or 'ERROR'
         """
        response = self.serverSocket.send(gameStatus.game.name + " ACCUSE " + playerName)
        if response[0] == "OK":
            return True
        return False

    def judge(self, playerName, playerNature):
        """
         Basic function that send the "JUDGE" command to the server
         :param: 'playerName', name of the player that I want to vote
         :param: 'playerNature', nature of the player
         :return: 'OK noted',  or 'ERROR'
         """
        response = self.serverSocket.send(gameStatus.game.name + " JUDGE " + playerName + ' ' + playerNature)
        #print('Risposta di judge: ' + response[0])
        if response[0] == "OK":
            return True
        return False

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
            print("Error. Game status from LOBBY to " + str(gameStatus.game.state) + gameStatus.game.me.name)
            return False
        return True

    def strategy(self, strategyType):
        """
        Strategies Dispatcher
        :param strategyType: the type of the strategy. Defined in Karen's init
        :return: -
        """
        pl = SD_Player(gameStatus.game.me.name, gameStatus.game.me.team)
        gameStatus.db.playerList[gameStatus.game.me.name] = pl
        threadino = ChatAnalysisThread(gameStatus.game.me.name)
        threadino.start()
        SD_thread = SocialDeductionThread()
        SD_thread.start()

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
        gameStatus.game.weightedMap = deterministicMap(self.maxWeight)

        while gameStatus.game.state != 'FINISHED' and gameStatus.game.me.state != "KILLED":
            if gameStatus.game.emergencyMeeting == 1:
                max_imp = None
                max_vote = 0
                for i in gameStatus.db.playerList.keys():
                    if gameStatus.game.me.name != gameStatus.db.playerList.get(i):
                        if gameStatus.db.playerList.get(i).sdScore > max_vote:
                            max_vote = gameStatus.db.playerList.get(i).sdScore
                            max_imp = gameStatus.db.playerList.get(i).name
                self.accuse(max_imp)
                gameStatus.game.emergencyMeeting = 0

            nextActions = lowLevelStrategy(self.maxWeight, gameStatus.game.wantedFlagX, gameStatus.game.wantedFlagY)

            for (action, direction) in nextActions:
                if action == "move":
                    self.move(direction)
                if action == "shoot":
                    self.shoot(direction)

            # AGGIORNAMENTO
            gameStatus.game.serverMap = self.lookAtMap(False)
            gameStatus.game.weightedMap = deterministicMap(self.maxWeight)
            self.lookStatus()

        if gameStatus.game.state != "FINISHED":
            print(gameStatus.game.me.name + " è morto.")

        while gameStatus.game.state == "ACTIVE":
            self.lookStatus()

        return True

    def fStrategy(self):
        """
        Call the fuzzyStrategy. Uses fuzzy rule to take the best decision.
        This function will check if you are an impostor or not and check in which is the game's stage
        :return:
        """
        TS_thread = TuringTestThread()
        TS_thread.start()
        gameStatus.game.serverMap = self.lookAtMap(True)
        gameStatus.game.weightedMap = deterministicMap(self.maxWeight)

        while gameStatus.game.state != 'FINISHED' and gameStatus.game.me.state != "KILLED":
            if gameStatus.game.emergencyMeeting == 1:
                max_imp = None
                max_vote = 0.2
                for i in gameStatus.db.playerList.keys():
                    if gameStatus.game.me.name != gameStatus.db.playerList.get(i):
                        if gameStatus.db.playerList.get(i).sdScore > max_vote:
                            max_vote = gameStatus.db.playerList.get(i).sdScore
                            max_imp = gameStatus.db.playerList.get(i).name
                if max_imp is not None:
                    self.accuse(max_imp)
                gameStatus.game.emergencyMeeting = 0
            # check the game stage and if i'm an impostor or not
            if gameStatus.game.me.loyalty == gameStatus.game.me.team:
                if gameStatus.game.stage == 0:
                    endx, endy, nearestEnemyDistance = FuzzyControlSystemStage0(self.maxWeight)
                elif gameStatus.game.stage == 1:
                    endx, endy, nearestEnemyDistance = FuzzyControlSystemStage1(self.maxWeight)
                else:
                    endx, endy, nearestEnemyDistance = FuzzyControlSystemStage2(self.maxWeight)
            else:
                if gameStatus.game.stage == 0:
                    endx, endy, nearestEnemyDistance = FuzzyControlSystemStage0(self.maxWeight)
                else:
                    endx, endy, nearestEnemyDistance = FuzzyControlSystemImpostor(self.maxWeight)
                print(gameStatus.game.me.name + " impostor")
            # Avoid useless LOOK if I can't die moving

            if gameStatus.game.stage == 0:
                for i in range(1, len(findPath(gameStatus.game.weightedMap, gameStatus.game.me, endx, endy))):
                    try:
                        direction, coordinates = gameStatus.game.me.movement.move(gameStatus.game.weightedMap,
                                                                                  gameStatus.game.me, endx, endy)
                        if direction is not None:
                            if self.move(direction):
                                gameStatus.game.me.x = coordinates[0]
                                gameStatus.game.me.y = coordinates[1]

                    except():
                        print("Exception generated by movement.move")



            elif int(nearestEnemyDistance // 2) > 2:
                for i in range(1, int(nearestEnemyDistance // 2)):
                    #se c'è qualcosa da votare vota uno else muoviti
                    if len(gameStatus.judgeList) > 0:
                        obj = gameStatus.judgeList.pop()
                        obj_name = obj[0]
                        obj_nature = obj[1]
                        print('DA MANDARE: ' + obj_name + ' ' + obj_nature + '\n')
                        self.judge(obj_name, obj_nature)
                    else:
                        try:
                            direction, coordinates = gameStatus.game.me.movement.move(gameStatus.game.weightedMap, gameStatus.game.me, endx, endy)
                            if direction is not None:
                                if self.move(direction):
                                    gameStatus.game.me.x = coordinates[0]
                                    gameStatus.game.me.y = coordinates[1]
                        except():
                            print("Exception generated by movement.move")

                    try:
                        direction, coordinates = gameStatus.game.me.movement.move(gameStatus.game.weightedMap,
                                                                                  gameStatus.game.me, endx, endy)
                        if direction is not None:
                            if self.move(direction):
                                gameStatus.game.me.x = coordinates[0]
                                gameStatus.game.me.y = coordinates[1]
                    except():
                        print("Exception generated by movement.move")
            else:
                if gameStatus.game.me.loyalty == gameStatus.game.me.team:

                    nextActions = lowLevelStrategy(self.maxWeight, endx, endy)
                else:
                    nextActions = lowLevelStrategyImpostor(self.maxWeight, endx, endy)
                    print(gameStatus.game.me.name + " impostor")

                for (action, direction) in nextActions:
                    if action == "move":
                        self.move(direction)
                    if action == "shoot":
                        self.shoot(direction)

            # AGGIORNAMENTO
            gameStatus.game.serverMap = self.lookAtMap(False)
            gameStatus.game.weightedMap = deterministicMap(self.maxWeight)

        if gameStatus.game.state != "FINISHED":
            print(gameStatus.game.me.name + " è morto.")

        while gameStatus.game.state == "ACTIVE":
            self.lookStatus()

        return True
