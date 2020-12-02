from random import randint
from karen import Karen
from threading import Thread
import time


class aKarenThread(Thread):

    def __init__(self, name, gameName):
        Thread.__init__(self)

        self.karen = Karen(name)
        self.name = name
        self.gameName = gameName

    def run(self):
        #tournamentName = input("Enter the name of the tournament you want to join: ")
        self.registerToTournament("SmartCup")
        #print("You joined the tournament " + tournamentName)
        joined = False
        while joined is False:
            joined = self.karen.joinGame(self.gameName, self.name, "AI", "AI02")
            if joined is True:
                self.karen.waitToStart()


    def registerToTournament(self, tournamentName):
        self.karen.chatSocket.sendInChat(tournamentName, "join")

    def joinMatch(self, gameName):
        self.karen.joinGame(gameName, self.name, "AI", "AI02")
        self.karen.waitToStart()


for i in range(0, 3):
    x = aKarenThread("Karen-AI-2" + str(i), "SmartCUP-12-1")
    x.start()
