from pprint import pprint

from movement import *
from connection.serverConnection import *
from data_structure.gameStatus import *
from connection.chatConnection import ConnectToChat
import configparser
import re


class Karen:
    """
    Karen identify the AI-subsystem that is able to play an AmongAIs match
    """

    def __init__(self, name):
        """
        Construct a new 'Karen' object.

        :param name: The name of the AI
        :return: returns nothing
        """

        # Identify the Karen as a Player
        self.me = Player(name)

        # A Karen can play one game at a time. Game encapsulate all the information about the map and other players
        self.game = Game(None)
        self.me.movement = rb_movement(movement)

        print("Hi, I am " + self.me.name)

        config = configparser.ConfigParser()
        config.read('config')

        self.host = config['connectionParam']['HOST']
        self.port = config['connectionParam']['PORT']
        self.delay = config['connectionParam']['DELAY']

        self.host_chat = config['chatParam']['HOST']
        self.port_chat = config['chatParam']['PORT']

        # Initialize the connection to the server and the chat system
        self.serverSocket = connectToServer(self.host, self.port, self.delay)

        self.ChatHOST = config['chatParam']['HOST']
        self.ChatPORT = config['chatParam']['PORT']

        self.chatSocket = ConnectToChat(self.ChatHOST, self.ChatPORT, self.me.name)

    def createGame(self, gameName):
        """
        Create a new Game
        :param gameName: uniquely identifies the game.
        :return: True if created, False ow.
        """
        response = self.serverSocket.send("NEW " + gameName)
        if response[0] == "OK Created":
            self.game.name = gameName
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

        if self.game.name is None:
            print("You are not in any game at the moment.")
            return False
        if reason is None:
            response = self.serverSocket.send(self.game.name + "LEAVE")
        else:
            response = self.serverSocket.send(self.game.name + "LEAVE" + " " + reason)
        if response[0] == "OK":
            print(self.me.name + " leaved the game " + self.game.name)
            self.game.name = None
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
        self.game.name = gameName
        self.me.nature = nature
        self.me.role = role
        self.me.userInfo = userInfo

        cmd = gameName + " JOIN " + self.me.name + " " + nature + " " + role
        if userInfo is not None:
            cmd += " " + userInfo

        response = self.serverSocket.send(cmd)

        if response[0].startswith("OK"):
            print(self.me.name + " joined the game " + self.game.name)
            row = re.split(' |=', response[0])
            self.me.team = row[2]
            self.me.loyalty = row[4]

            self.chatSocket.connectToChannel(self.game.name)
            return True

        else:
            self.game.name = None
            print(self.me.name + ": " + response[0])
            return False

    def startGame(self):
        """
        Send Start command to the server. Only the AI who create the room can start the game.
        :return: True if the game started, False ow.
        """
        self.lookStatus()
        response = self.serverSocket.send(self.game.name + " START")

        if response[0] == 'OK Game started':
            print(self.game.name + " started.")

            return self.waitToStart()
        else:
            print(self.game.name + " " + response[0])
            return False

    def lookStatus(self):
        """
        Retrieve information about the game status and of all the player (allies and enemies) in that room.
        :return: True if information updated, False ow.
        """
        response = self.serverSocket.send(self.game.name + " STATUS")

        if response[0] == 'OK LONG':
            for s in range(0, len(response)):
                # Parse information about the Game
                if response[s].startswith("GA:"):
                    row = re.split(' |=', response[s])
                    self.game.name = row[2]
                    self.game.state = row[4]
                    self.game.size = row[6]

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
                        if self.game.allies.get(row[2]) is None and self.game.enemies.get(row[2]) is None:
                            pl = Player(row[4])
                            pl.symbol = row[2]
                            pl.team = row[6]
                            pl.x = int(row[8])
                            pl.y = int(row[10])
                            pl.state = row[12]
                            if pl.team == self.me.team:
                                self.game.allies[pl.symbol] = pl
                            else:
                                self.game.enemies[pl.symbol] = pl

                        elif self.game.allies.get(row[2]) is not None:
                            self.game.allies.get(row[2]).x = int(row[8])
                            self.game.allies.get(row[2]).y = int(row[10])
                            self.game.allies.get(row[2]).state = row[12]


                        elif self.game.enemies.get(row[2]) is not None:
                            self.game.enemies.get(row[2]).x = int(row[8])
                            self.game.enemies.get(row[2]).y = int(row[10])
                            self.game.enemies.get(row[2]).state = row[12]

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
        response = self.serverSocket.send(self.game.name + " LOOK")

        if response[0] == 'OK LONG':
            response.pop(0)
            response.pop(len(response) - 1)
            actualMap = []

            for i in range(0, len(response)):

                splitted = split(response[i])
                for j in range(0, len(splitted)):
                    # For each symbol in the map, check if it identifies a player. If so, update its position information
                    if self.game.allies.get(splitted[j]) is not None:
                        self.game.allies.get(splitted[j]).x = j
                        self.game.allies.get(splitted[j]).y = i

                    elif self.game.enemies.get(splitted[j]) is not None:
                        self.game.enemies.get(splitted[j]).x = j
                        self.game.enemies.get(splitted[j]).y = i
                    elif self.me.symbol == splitted[j]:
                        self.me.x = j
                        self.me.y = i

                    # Used only the first time that Karen looks at the map. Find FLAGS position
                    elif firstTime is True:

                        if splitted[j] == "x" and self.me.symbol.isupper():
                            self.game.wantedFlagName = "x"
                            self.game.wantedFlagX = j
                            self.game.wantedFlagY = i
                        elif splitted[j] == "x" and self.me.symbol.islower():
                            self.game.toBeDefendedFlagName = "x"
                            self.game.toBeDefendedFlagX = j
                            self.game.toBeDefendedFlagY = i
                        elif splitted[j] == "X" and self.me.symbol.islower():
                            self.game.wantedFlagName = "X"
                            self.game.wantedFlagX = j
                            self.game.wantedFlagY = i
                        elif splitted[j] == "X" and self.me.symbol.isupper():
                            self.game.toBeDefendedFlagName = "X"
                            self.game.toBeDefendedFlagX = j
                            self.game.toBeDefendedFlagY = i

                actualMap.append(splitted)

            return actualMap

        else:
            return None

    def nop(self):
        """
        Send a NOP command. (keep alive control)
        :return:
        """
        return self.serverSocket.send(self.game.name + " NOP ")

    def move(self, direction):
        """
         Basic function that send the "MOOVE" command to the server
         :param direction: define where the AI wants to move.
         :return: 'OK moved', 'Ok blocked' or 'ERROR'
         """
        return self.serverSocket.send(self.game.name + " MOVE " + direction)

    def shoot(self, direction):
        """
        Basic function that send the "SHOOT" command to the server
        :param direction: define where the AI wants to shoot.
        :return: 'OK x' where x is the position where the bullet landed
        """
        return self.serverSocket.send(self.game.name + " SHOOT " + direction)

    def waitToStart(self):
        """
        Wait until the game start.
        :return: start strategy if started. False on ERROR.
        """
        self.lookStatus()
        while self.game.state == "LOBBY":
            self.lookStatus()

        if self.game.state == "ACTIVE":
            self.fuzzyStrategy()
        else:
            print("Error. Game status from LOBBY to " + str(self.game.state))
            return False

    def deterministicMap(self):
        """
         CELLULAR AUTOMATA MAP. Discourage Karen to allign with enemies. If there is no other way, go and shoot.
         :param actualMap: the map retrieved from the server.
         :return: a weighted map
         """

        value = ["9", "6"]
        walkable = ["."]
        river = ["~"]
        trap = ["!"]
        obstacles = ["#", "@"]
        recharge = ["$"]
        barrier = ["&"]
        allies = self.game.allies.keys()
        enemies = self.game.enemies.keys()
        serverMap = self.game.serverMap
        weightedMap = serverMap

        def recursiveMap(i, j, rec_weightedMap, weight):
            '''
            Recursive map generation. Resamble Cellular Automata decision adding weight to the map consistently with the distance from enemies
            :param i: the horizontal coordinate
            :param j: the vertical coordinate
            :param rec_weightedMap: the map
            :param weight: the weight of being in [i:,:j] position
            :return: a weighted map
            '''
            # da  muro a nemico
            for position in range(enemy.x, -1, -1):
                if rec_weightedMap[i][position] != '#' and rec_weightedMap[i][position] != "&":
                    if isinstance(rec_weightedMap[i][position], int) is False:
                        rec_weightedMap[i][position] = weight
                else:
                    break

            # da nemico a muro
            for position in range(enemy.x, len(rec_weightedMap[i])):
                if rec_weightedMap[i][position] != '#' and rec_weightedMap[i][position] != "&":
                    if isinstance(rec_weightedMap[i][position], int) is False:
                        rec_weightedMap[i][position] = weight
                else:
                    break

            # Controllo per colonne
            for position in range(enemy.y, -1, -1):
                if rec_weightedMap[position][j] != '#' and rec_weightedMap[position][j] != "&":
                    if isinstance(rec_weightedMap[position][j], int) is False:
                        rec_weightedMap[position][j] = weight
                else:
                    break

            for position in range(enemy.y, len(rec_weightedMap[j])):
                if rec_weightedMap[position][j] != '#' and rec_weightedMap[position][j] != "&":
                    if isinstance(rec_weightedMap[position][j], int) is False:
                        rec_weightedMap[position][j] = weight
                else:
                    break

            return rec_weightedMap

        # ---------------------------------------------------------------------------------------------------
        # For each enemy that is still alive, create a weighted map assigning value to all the position in the map around the enemy
        for enemykey in self.game.enemies.keys():
            enemy = self.game.enemies.get(enemykey)
            if enemy.state == "ACTIVE":
                # First call to assign weight to the enemy's 'x column' and 'y row' coordinate
                weightedMap = recursiveMap(enemy.y, enemy.x, serverMap, 9)

                # Recursive calls giving the already weighted to assign weight to all the coordinate around the enemy player
                if enemy.y - 1 >= 0:
                    if enemy.x - 1 >= 0:
                        weightedMap = recursiveMap(enemy.y - 1, enemy.x - 1, weightedMap, 6)
                    if enemy.x + 1 < len(weightedMap[0]):
                        weightedMap = recursiveMap(enemy.y - 1, enemy.x + 1, weightedMap, 6)

                if enemy.y + 1 < len(weightedMap[0]):
                    if enemy.x - 1 >= 0:
                        weightedMap = recursiveMap(enemy.y + 1, enemy.x - 1, weightedMap, 6)
                    if enemy.x + 1 < len(weightedMap[0]):
                        weightedMap = recursiveMap(enemy.y + 1, enemy.x + 1, weightedMap, 6)

        # For each position, assign different weight considering their nature
        for i in range(0, len(serverMap[0])):
            for j in range(0, len(serverMap[0])):

                if weightedMap[i][j] in value:
                    None

                elif serverMap[i][j] in walkable:
                    weightedMap[i][j] = 1

                elif serverMap[i][j] in river:
                    weightedMap[i][j] = 25

                elif serverMap[i][j] in trap:
                    weightedMap[i][j] = 32

                elif serverMap[i][j] in obstacles:
                    weightedMap[i][j] = 0

                elif serverMap[i][j] in recharge:
                    weightedMap[i][j] = 1

                elif serverMap[i][j] in barrier:
                    weightedMap[i][j] = 0

                elif serverMap[i][j] == self.game.wantedFlagName:
                    weightedMap[i][j] = 1

                elif serverMap[i][j] == self.game.toBeDefendedFlagName:
                    weightedMap[i][j] = 0

                elif serverMap[i][j] in allies or serverMap[i][j] in enemies or serverMap[i][j] == self.me.symbol:
                    weightedMap[i][j] = 1

        return weightedMap

    def act(self, endx, endy):
        """
        Basic action function
        :return: True when the game ends or the action is completed.
        """


        while self.game.state != 'FINISHED' and self.me.state != "KILLED":
            direction = self.me.movement.move(self.game.weightedMap, self.me, endx, endy)

            # se sto in linea con altri, sparo
            for key in self.game.enemies:
                enemy = self.game.enemies.get(key)

                if enemy.state == "ACTIVE":
                    if self.me.x == enemy.x:
                        self.chatSocket.sendInChat(self.game.name, enemy.name + " I kill u bastard!!! RATATATAAAAAAA")
                        if self.me.y > enemy.y:
                            self.shoot("N")
                        else:
                            self.shoot("S")
                    elif self.me.y == enemy.y:
                        self.chatSocket.sendInChat(self.game.name, enemy.name + " I kill u bastard!!! RATATATAAAAAAA")

                        if self.me.x > enemy.x:
                            self.shoot("W")
                        else:
                            self.shoot("E")

            # controllo se andrò in linea di tiro
            if direction == "E" and self.game.weightedMap[self.me.y][self.me.x + 1] == "9":

                # my x becomes  x+1
                if self.game.serverMap[self.me.y][self.me.x + 1] == "~":
                    self.move(direction)

                else:
                    for key in self.game.enemies:
                        enemy = self.game.enemies.get(key)

                        if enemy.x == self.me.x + 1:

                            if enemy.y >= self.me.y:
                                # muoviti ad est e spara a sud
                                print(self.me.name + " si muove a: " + direction + " e spara a sud")

                                self.move(direction)
                                self.shoot("S")
                            if enemy.y < self.me.y:
                                # muoviti ad est e spara a nord
                                print(self.me.name + " si muove a: " + direction + " e spara a nord")

                                self.move(direction)
                                self.shoot("N")

            elif direction == "W" and self.game.weightedMap[self.me.y][self.me.x - 1] == "9":

                # my x becomes  x-1
                if self.game.serverMap[self.me.y][self.me.x - 1] == "~":
                    self.move(direction)

                else:
                    for key in self.game.enemies:
                        enemy = self.game.enemies.get(key)

                        if enemy.x == self.me.x - 1:

                            if enemy.y >= self.me.y:
                                # muoviti ad ovest e spara a sud
                                print(self.me.name + " si muove a: " + direction + " e spara a sud")

                                self.move(direction)
                                self.shoot("S")
                            if enemy.y < self.me.y:
                                # muoviti ad ovest e spara a nord
                                print(self.me.name + " si muove a: " + direction + " e spara a nord")

                                self.move(direction)
                                self.shoot("N")

            elif direction == "S" and self.game.weightedMap[self.me.y + 1][self.me.x] == "9":

                # my y becomes  y+1
                if self.game.serverMap[self.me.y + 1][self.me.x] == "~":
                    self.move(direction)

                else:
                    for key in self.game.enemies.keys():
                        enemy = self.game.enemies.get(key)

                        if enemy.y == self.me.y + 1:

                            if enemy.x >= self.me.x:
                                print(self.me.name + " si muove a: " + direction + " e spara a est")

                                self.move(direction)
                                self.shoot("E")
                            if enemy.x < self.me.x:
                                # muoviti a sud e spara ad ovest
                                print(self.me.name + " si muove a: " + direction + " e spara a ovest")

                                self.move(direction)
                                self.shoot("W")


            elif direction == "N" and self.game.weightedMap[self.me.y - 1][self.me.x] == "9":

                # my y becomes  y-1
                if self.game.serverMap[self.me.y - 1][self.me.x] == "~":
                    self.move(direction)

                else:
                    for key in self.game.enemies:
                        enemy = self.game.enemies.get(key)

                        if enemy.y == self.me.y - 1:

                            if enemy.x > self.me.x:
                                # muoviti ad nord e spara ad est
                                print(self.me.name + " si muove a: " + direction + " e spara a est")

                                self.move(direction)
                                self.shoot("E")
                            if enemy.x < self.me.x:
                                # muoviti a nord e spara ad ovest
                                print(self.me.name + " si muove a: " + direction + " e spara a ovest")
                                self.move(direction)
                                self.shoot("W")

            # Non sono andato in linea di tiro
            else:
                self.move(direction)

            # AGGIORNAMENTO
            self.game.serverMap = self.lookAtMap(False)
            self.game.weightedMap = self.deterministicMap()
            self.lookStatus()
            # riparte il while


        if(self.game.state != "FINISHED"):
            print(self.me.name + " è morto.")

        while self.game.state == "ACTIVE":
            self.lookStatus()

        return True

    def fuzzyStrategy(self):

        self.lookStatus()

        self.game.serverMap = self.lookAtMap(True)
        self.game.weightedMap = self.deterministicMap()

        self.act(self.game.wantedFlagX, self.game.wantedFlagY)
