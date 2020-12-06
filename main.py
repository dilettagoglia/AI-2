from multiprocessing import Process
from random import randint

from karen import *

"""
Nuovo main per creare karen multi processo e non multithreading
"""


def creator(name, gameName):
    print(name)
    k = Karen(name, 'fuzzyStrategy')
    time.sleep(0.5)
    if k.createGame(gameName, "TBQ1"):
        k.joinGame(gameName, name, "AI", "AI-02")
        while True:
            time.sleep(2)
            k.startGame()


def gamer(name, gameName):
    print(name)
    k = Karen(name, 'fuzzyStrategy')
    k.joinGame(gameName, name, "AI", "AI-02")
    result = k.waitToStart()


if __name__ == '__main__':
    var = str(randint(100000, 900000))
    process = []
    p = (Process(target=creator, args=('KarenOwner', var)))
    p.start()
    process.append(p)
    time.sleep(1)

    for i in range(0, 25):
        p = Process(target=gamer, args=('Karen' + str(i), var))
        p.start()
        process.append(p)

    for p in process:
        p.join()
