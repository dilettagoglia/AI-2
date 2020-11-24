from random import randint
from karen import Karen
from threading import Thread
import time

gameName = str(randint(100000, 900000))


class aKarenThread(Thread):

    def __init__(self, name):
        Thread.__init__(self)

        self.karen = Karen(name)
        self.name = name

    def run(self):
        self.karen.joinGame(gameName, self.name, "AI", "-")
        self.karen.waitToStart()


karen1 = Karen("imtheowner")


if karen1.createGame(gameName):
    karen1.joinGame(gameName, "imtheowner", "AI", "-")

    for i in range(1, 20):
        x = aKarenThread("pinko" + str(i))
        x.start()

    time.sleep(1)
    karen1.startGame()
