from movement import *
from serverConnection import *
from data_structure.gameStatus import *
from pprint import pprint
import configparser

import re


class Karen:

    # Define the AI fundamental values
    def __init__(self, name):

        self.me = Player(name)

        self.game = Game(None)
        self.game.me = self.me
        self.movement = rb_movement(movement)
        print("Hi, I am " + self.me.name)

        config = configparser.ConfigParser()
        config.read('config')

        self.host = config['connectionParam']['HOST']
        self.port = config['connectionParam']['PORT']

        self.serverSocket = connectToServer(self.host, self.port)

    # Create a new game room.
    # @return True if created, False if not
    def createGame(self, gameName):
        response = self.serverSocket.send("NEW " + gameName)
        if (response[0] == "OK Created"):
            print(self.me.name + " created a game room: " + gameName)
            return True
        else:
            print(response)
            return False

    # Let the AI leave a game room (works only if game started)
    # currently doesn't work [ERROR 404 Game not found]
    def leaveGame(self, reason=None):
        if (self.game.name is None):
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

    # Let the AI join a game room.
    # @return True if joined, False otherwise
    def joinGame(self, gameName, nature, role, userInfo=None):
        # <game> JOIN <player-name> <nature> <role> <user-info>
        self.game.name = gameName
        cmd = gameName + " JOIN " + self.me.name + " " + nature + " " + role
        if userInfo is not None:
            cmd += " " + userInfo

        response = self.serverSocket.send(cmd)
        if response[0] == "OK Joined":
            print(self.me.name + " joined the game " + self.game.name)
            return True

        else:
            self.game.name = None
            print(self.me.name + ": " + response[0])
            return False

    # Only the AI who create the room can start the game.
    # @return True if game is started, False otherwise
    def startGame(self):
        response = self.serverSocket.send(self.game.name + " START")

        if response[0] == 'OK Game started':
            print(self.game.name + " started.")

            # chiama lookstatus
            # chiama strategy
            return True
        else:
            print(self.game.name + " " + response[0])
            return False

    # Let the AI to know the status of the game room and of all the player
    def lookStatus(self):
        response = self.serverSocket.send(self.game.name + " STATUS")
        if response[0] == 'OK LONG':
            for s in range(1, len(response) - 1):
                print(response[s])
                if response[s].startswith("GA:"):
                    row = re.split(' |=', response[s])
                    self.game.name = row[2]
                    self.game.state = row[4]
                    self.game.size = row[6]
                elif response[s].startswith("ME:"):
                    row = re.split(' |=', response[s])
                    self.me.symbol = row[2]
                    self.me.name = row[4]
                    self.me.team = row[6]
                    self.me.loyalty = row[8]
                    self.me.energy = row[10]
                    self.me.score = row[12]
                elif response[s].startswith("PL:"):
                    row = re.split(' |=', response[s])
                    if row[2] == self.me.symbol:
                        self.me.x = row[8]
                        self.me.y = row[10]
                    else:
                        if self.game.allies.get(row[2]) is None and self.game.allies.get(row[2]) is None:
                            pl = Player(row[4])
                            pl.symbol = row[2]
                            pl.team = row[6]
                            pl.x = row[8]
                            pl.y = row[10]
                            if (pl.team == self.me.team):
                                print("alleato")
                                self.game.allies[pl.symbol] = pl
                            else:
                                print("nemico")
                                self.game.enemies[pl.symbol] = pl

                        elif self.game.allies.get(row[2]) is not None:
                            self.game.allies.get(row[2]).x = row[8]
                            self.game.allies.get(row[2]).y = row[10]

                        elif self.game.enemies.get(row[2]) is not None:
                            self.game.enemies.get(row[2]).x = row[8]
                            self.game.enemies.get(row[2]).y = row[10]


    # Let the AI to look at the map (works only if the game started)
    def lookAtMap(self, firstTime):
        response = self.serverSocket.send(self.game.name + " LOOK")
        # parse the map in a matrix-formatted form and return it
        if (response[0] == 'OK LONG'):
            actualMap = self.parseMap(response, firstTime)
        else:
            return None
        return actualMap

    # Let the AI to move around the map.
    # @return 'Ok moved' or 'Error'
    def move(self, direction):
        return self.serverSocket.send(self.game.name + " MOVE " + direction)

    # Let the AI to shoot
    # @return 'OK x' where x is the position where the bullet landed
    def shoot(self, direction):
        return self.serverSocket.send(self.game.name + " SHOOT " + direction)

    # This function parse the recieved LIST in a well formatted map
    def parseMap(self, input, firstTime):
        def split(word):
            return [char for char in word]

        # input = eval(input)
        input.pop(0)
        input.pop(len(input) - 1)
        mymap = []

        for i in range(0,len(input)):
            splitted = split(input[i])
            for j in range(0, len(splitted)):

                if self.game.allies.get(splitted[j]) is not None:
                    self.game.allies.get(splitted[j]).x = j
                    self.game.allies.get(splitted[j]).y = i

                elif self.game.enemies.get(splitted[j]) is not None:
                    self.game.enemies.get(splitted[j]).x = j
                    self.game.enemies.get(splitted[j]).y = i
                elif self.me.symbol == splitted[j]:
                    self.me.x = j
                    self.me.y = i
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


            mymap.append(splitted)
        return mymap

    # La strategia decide la prossima operazione da fare.
    # In particolare decide SE devo muovermi, la classe movement decide il DOVE.
    # Ottenuta la risposta dal server, guardo nuovamente la mappa e ricomincio a ragionare
    # response = self.move("test", direction)
    # response = self.lookAtMap("test")

    def waitToStart(self):
        # lookstatus finchè state non è active
        # chiama strategy
        return None


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
        pprint(vars(self.me))

        actualMap = self.lookAtMap(True)

        while(True):
            if(actualMap is not None):
                direction = self.movement.move(actualMap, self.me, self.game, self.game.wantedFlagX, self.game.wantedFlagY)
                print("Mi muovo verso: " + direction)
                print(str(self.shoot(direction)))

                actualMap = self.lookAtMap(False)
                #pprint(vars(self.me))


        # print("Map len: " + str(len(actualMap)))
        # chiudi ciclo
