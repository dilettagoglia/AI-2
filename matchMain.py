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
        self.karen.joinGame(self.gameName, self.name, "AI", "-")
        self.karen.waitToStart()


for i in range(0, 3):
    x = aKarenThread("Karen-" + str(i), "test10")
    x.start()

