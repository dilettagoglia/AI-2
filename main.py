from random import randint
from karen import Karen
from threading import Thread
import time
gameName = str(randint(100000, 900000))


class aKarenThread (Thread):

    def __init__(self, name):
        Thread.__init__(self)

        self.karen = Karen(name)
        self.name = name

    def run(self):

        self.karen.joinGame(gameName, self.name, "AI", "-")
        self.karen.waitToStart()

karen1 = Karen("imtheowner")


t1 = aKarenThread("AI-02")
t2 = aKarenThread("panko")
t3 = aKarenThread("ponko")
t4 = aKarenThread("punko")
t5 = aKarenThread("penko")
if karen1.createGame(gameName):
    if karen1.joinGame(gameName, "imtheowner", "AI", "-"):
        t1.start()
        t2.start()
        t3.start()
        t4.start()
        t5.start()
        time.sleep(8)
        karen1.startGame()

    t1.join()
    t2.join()