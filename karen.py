from movement import *
from connection.serverConnection import *
from data_structure.gameStatus import *
from pprint import pprint
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
        self.game.me = self.me
        self.movement = rb_movement(movement)

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
        # self.chatSocket = ConnectToChat(self.host_chat, self.port_chat, self.me.name)

    def createGame(self, gameName):
        """
        Create a new Game
        :param gameName: uniquely identifies the game.
        :return: True if created, False ow.
        """
        response = self.serverSocket.send("NEW " + gameName)
        if response[0] == "OK Created":
            self.game.name = gameName
            self.game.me = self.me
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
        cmd = gameName + " JOIN " + self.me.name + " " + nature + " " + role
        if userInfo is not None:
            cmd += " " + userInfo

        response = self.serverSocket.send(cmd)
        if response[0] == "OK Joined":
            print(self.me.name + " joined the game " + self.game.name)
            self.game.me = self.me
            # If the player joined the game, wait until the game state change to ACTIVE then start strategy.
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

                    # Not Karen, update information of other players
                    else:
                        if self.game.allies.get(row[2]) is None and self.game.allies.get(row[2]) is None:
                            pl = Player(row[4])
                            pl.symbol = row[2]
                            pl.team = row[6]
                            pl.x = int(row[8])
                            pl.y = int(row[10])
                            if pl.team == self.me.team:
                                self.game.allies[pl.symbol] = pl
                            else:
                                self.game.enemies[pl.symbol] = pl

                        elif self.game.allies.get(row[2]) is not None:
                            self.game.allies.get(row[2]).x = int(row[8])
                            self.game.allies.get(row[2]).y = int(row[10])

                        elif self.game.enemies.get(row[2]) is not None:
                            self.game.enemies.get(row[2]).x = int(row[8])
                            self.game.enemies.get(row[2]).y = int(row[10])

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

        if (response[0] == 'OK LONG'):
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

        self.lookStatus()
        while self.game.state == "LOBBY":
            self.lookStatus()

        if self.game.state == "ACTIVE":
            self.strategy()
        else:
            print("Error. Game status from LOBBY to " + str(self.game.state))
            return False

    def defensiveMap(self, actualMap):

        for enemykey in self.game.enemies.keys():
            enemy = self.game.enemies.get(enemykey)
            # print("Considero nemico in pos " + str(enemy.y) + " " + str(enemy.x))

            # Controllo per righe
            i = enemy.y
            # da  muro a nemico
            for position in range(enemy.x, -1, -1):
                if (actualMap[i][position] != '#'):
                    actualMap[i][position] = str(9)
                else:
                    break

            # da nemico a muro
            for position in range(enemy.x, len(actualMap[i])):
                if (actualMap[i][position] != '#'):
                    actualMap[i][position] = str(9)
                else:
                    break

            # Controllo per colonne
            j = enemy.x
            for position in range(enemy.y, -1, -1):
                if (actualMap[position][j] != '#'):
                    actualMap[position][j] = str(9)
                else:
                    break

            for position in range(enemy.y, len(actualMap[j])):
                if (actualMap[position][j] != '#'):
                    actualMap[position][j] = str(9)
                else:
                    break

        return actualMap

    def strategy(self):

        # if ctf
        # if search recharge
        # going for killing

        # start timer
        # ciclo
        # ragiona
        # wait timer > 500ms riparti col ciclo
        # restart timer
        # direction = self.movement.move()
        self.lookStatus()
        # pprint(vars(self.me))

        actualMap = self.lookAtMap(True)
        parse = self.defensiveMap(actualMap)

        opBeforeNextLookStatus = 10
        while self.game.state != 'FINISHED':
            if (actualMap is not None):
                direction = self.movement.move(actualMap, self.me, self.game, self.game.wantedFlagX,
                                               self.game.wantedFlagY)

                # se facendo questa mossa sarò in linea, move & shoot. (controlla se sto in fiume)

                # print("Mi muovo verso: " + direction)
                print(str(self.move(direction)))
                opBeforeNextLookStatus -= 1

                actualMap = self.lookAtMap(False)

                # se sto in linea e non c'è muro spara  (controlla se sto in fiume)

                actualMap = self.defensiveMap(actualMap)

                if (opBeforeNextLookStatus == 0):
                    self.lookStatus()
                    opBeforeNextLookStatus = 10

        return True
