from movement import *

from serverConnection import connectToServer
import configparser

class karen():

    def __init__(self, name):
        self.name = name
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

    def leaveGame(self, gameName):
        response = self.serverSocket.send("LEAVE " + gameName)
        if (response[0] == "OK"):
            print(gameName + " leaved.")
        else:
            print(response)

        return response

    def joinGame(self, gameName, playerName, nature, role, userInfo=None):
        # <game> JOIN <player-name> <nature> <role> <user-info>
        cmd = gameName + " JOIN " + playerName + " " + nature + " " + role
        if userInfo is not None:
            cmd += " " + userInfo

        response = self.serverSocket.send(cmd)
        if (response[0] == "OK Joined"):
            print(gameName + " joined.")
        else:
            print(response)

        return response

    def startGame(self, gameName):
        response = self.serverSocket.send(gameName + " START")
        # controllo 'OK'
        if(response[0]=='OK'):
            print("Game started.")
        else:
            print(response)

        return response

    def lookStatus(self, gameName):
        response = self.serverSocket.send(gameName+" STATUS")
        print(response)

    def lookAtMap(self, gameName):
        return self.serverSocket.send(gameName+" LOOK")

    def move(self, gameName, direction):
        return self.serverSocket.send(gameName+" MOVE " + direction)

    def shoot(self, gameName, direction):
        return self.serverSocket.send(gameName+" SHOOT " + direction)


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

        response = self.move("444", direction)
        print(response)
        #response = self.lookAtMap("test")



        #chiudi ciclo





