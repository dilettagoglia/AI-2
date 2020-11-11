from movement import *

from serverConnection import connectToServer
import configparser


class Karen:

    def __init__(self, name):
        self.name = name
        self.gameName = None
        self.movement = rand_movement(None)
        print("I am " + self.name)

        config = configparser.ConfigParser()
        config.read('config')

        self.host = config['connectionParam']['HOST']
        self.port = config['connectionParam']['PORT']

        self.serverSocket = connectToServer(self.host, self.port)


    def createGame(self, gameName):
        response = self.serverSocket.send("NEW " + gameName)
        if(response[0] == "OK Created"):
           print(gameName + " created.")
        else:
            print(response)

        return response

    def leaveGame(self, reason=None):
        if(self.gameName is None):
            print("You are not in any game at the moment.")
            return "OK"
        if reason is None:
            response = self.serverSocket.send(self.gameName + "LEAVE" + " " + reason)
        else:
            response = self.serverSocket.send(self.gameName + "LEAVE" + " " + reason)

        if response[0] == "OK":
            print(self.gameName + " leaved.")
            gameName = None
        else:
            print(response)

        return response

    def joinGame(self, gameName, nature, role, userInfo=None):
        # <game> JOIN <player-name> <nature> <role> <user-info>
        self.gameName = gameName
        cmd = gameName + " JOIN " + self.name + " " + nature + " " + role
        if userInfo is not None:
            cmd += " " + userInfo

        response = self.serverSocket.send(cmd)
        if response[0] == "OK Joined":
            print(gameName + " joined.")
        else:
            self.gameName = None
            print(response)

        return response

    def startGame(self):
        response = self.serverSocket.send(self.gameName + " START")
        # controllo 'OK'
        if response[0]=='OK':
            print("Game started.")
        else:
            print(response)

        return response

    def lookStatus(self):
        response = self.serverSocket.send(self.gameName+" STATUS")
        print(response)

    def lookAtMap(self):
        response = self.serverSocket.send(self.gameName+" LOOK")
        #parse the map in a matrix-formatted form and return it
        return response

    def move(self, direction):
        return self.serverSocket.send(self.gameName+" MOVE " + direction)

    def shoot(self, direction):
        return self.serverSocket.send(self.gameName+" SHOOT " + direction)


    # La strategia decide la prossima operazione da fare.
    # In particolare decide SE devo muovermi, la classe movement decide il DOVE.
    # Ottenuta la risposta dal server, guardo nuovamente la mappa e ricomincio a ragionare
    # response = self.move("test", direction)
    # response = self.lookAtMap("test")

    def strategy(self):
        # start timer
        # ciclo

        # ragiona
        # wait timer > 500ms riparti col ciclo
        # restart timer
        direction = self.movement.move()

        response = self.move(direction)
        print(response)
        #response = self.lookAtMap("test")



        #chiudi ciclo





