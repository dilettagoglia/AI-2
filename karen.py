from movement import *
from serverConnection import *
import configparser


class Karen:

    # Define the AI fundamental values
    def __init__(self, name):

        self.name = name
        self.symbol = None
        self.team = None
        self.loyalty = None
        self.energy = None
        self.score = None

        self.gameName = None

        self.movement = rb_movement(movement)
        print("Hi, I am " + self.name)

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
            print(self.name + " created a game room: " + gameName)
            return True
        else:
            print(response)
            return False

    # Let the AI leave a game room (works only if game started)
    # currently doesn't work [ERROR 404 Game not found]
    def leaveGame(self, reason=None):
        if (self.gameName is None):
            print("You are not in any game at the moment.")
            return False
        if reason is None:
            response = self.serverSocket.send(self.gameName + "LEAVE")
        else:
            response = self.serverSocket.send(self.gameName + "LEAVE" + " " + reason)
        if response[0] == "OK":
            print(self.name + " leaved the game " + self.gameName)
            gameName = None
            return True
        else:
            print(self.name + ": " + response[0])
            return False

    # Let the AI join a game room.
    # @return True if joined, False otherwise
    def joinGame(self, gameName, nature, role, userInfo=None):
        # <game> JOIN <player-name> <nature> <role> <user-info>
        self.gameName = gameName
        cmd = gameName + " JOIN " + self.name + " " + nature + " " + role
        if userInfo is not None:
            cmd += " " + userInfo

        response = self.serverSocket.send(cmd)
        if response[0] == "OK Joined":
            print(self.name + " joined the game " + self.gameName)
            return True

        else:
            self.gameName = None
            print(self.name + ": " + response[0])
            return False

    # Only the AI who create the room can start the game.
    # @return True if game is started, False otherwise
    def startGame(self):
        response = self.serverSocket.send(self.gameName + " START")

        if response[0] == 'OK Game started':
            print(self.gameName + " started.")
            return True
        else:
            print(self.gameName + " " + response[0])
            return False

    # Let the AI to know the status of the game room and of all the player
    def lookStatus(self):
        response = self.serverSocket.send(self.gameName + " STATUS")

        print(response)

    # Let the AI to look at the map (works only if the game started)
    def lookAtMap(self):
        response = self.serverSocket.send(self.gameName + " LOOK")
        # parse the map in a matrix-formatted form and return it
        return response

    # Let the AI to move around the map.
    # @return 'Ok moved' or 'Error'
    def move(self, direction):
        return self.serverSocket.send(self.gameName + " MOVE " + direction)

    # Let the AI to shoot
    # @return 'OK x' where x is the position where the bullet landed
    def shoot(self, direction):
        return self.serverSocket.send(self.gameName + " SHOOT " + direction)


    # This function parse the recieved LIST in a well formatted map
    def parseMap(self, input):
        def split(word):
            return [char for char in word]

        #input = eval(input)
        input.pop(0)
        input.pop(len(input)-1)
        mymap = []

        for row in input:
            mymap.append(split(row))
        return mymap


    # La strategia decide la prossima operazione da fare.
    # In particolare decide SE devo muovermi, la classe movement decide il DOVE.
    # Ottenuta la risposta dal server, guardo nuovamente la mappa e ricomincio a ragionare
    # response = self.move("test", direction)
    # response = self.lookAtMap("test")



    def strategy(self):

        #if ctf
        #if search recharge
        #going for killing

        # start timer
        # ciclo
        # ragiona
        # wait timer > 500ms riparti col ciclo
        # restart timer
        #direction = self.movement.move()

        response = self.lookAtMap()
        if(response[0]=='OK LONG'):
            actualMap = self.parseMap(response)

            direction = self.movement.move(actualMap, 2, 2 , 2 , 4)
            print(direction)

        response = self.lookAtMap()
        if (response[0] == 'OK LONG'):
            actualMap = self.parseMap(response)
            print (actualMap)
        #print("Map len: " + str(len(actualMap)))
        # chiudi ciclo
