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
        tournamentName = input("Enter the name of the tournament you want to join: ")
        self.registerToTournament(tournamentName)
        print("You joined the tournament " + tournamentName)

        matchName = input("Enter the match name you have to play (join): ")
        self.joinMatch(matchName)


    def registerToTournament(self, tournamentName):
        self.karen.chatSocket.sendInChat(tournamentName, "join")

    def joinMatch(self, gameName):
        self.karen.joinGame(gameName, self.name, "AI", "AI02")
        self.karen.waitToStart()

for i in range(0, 1):
    x = aKarenThread("Karen-AI-2" + str(i), "test10")
    x.start()

