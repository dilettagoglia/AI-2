# karen1 = karen('karen1')
# res1 = karen1.createGame(x)
# res1 = karen1.joinGame(x)
# res1 = karen1.startGame()

# karen2 = karen('karen2')
# res2 = karen2.joinGame(x)
# res2 = karen2.startGame()
# dichiaro che sono pronto con START. Il server risponde OK solo quando il gioco inizia effettivamente
# a questo punto inizia la mia strategia karen1.strategy()
from random import randint
from karen import Karen

gameName = str(randint(100000, 900000))
myname = "pinko"

karen1 = Karen("imtheowner")
karen2 = Karen(myname)

if karen1.createGame(gameName) :
    karen1.joinGame(gameName, "imtheowner", "AI", "-")
    karen2.joinGame(gameName, myname, "AI", "-")

    #se creatore, start dopo un po, altrimenti chiama waitToStart
    if karen1.startGame():
        karen1.strategy()
