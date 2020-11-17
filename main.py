from random import randint
from karen import Karen
import time
gameName = str(randint(100000, 900000))

karen1 = Karen("imtheowner")
karen2 = Karen("pinko")
karen3 = Karen("panko")

if karen1.createGame(gameName):
    karen1.joinGame(gameName, "imtheowner", "AI", "-")
    karen2.joinGame(gameName, "pinko", "AI", "-")
    karen3.joinGame(gameName, "panko", "AI", "-")

    #fare le join per
    karen1.startGame()
