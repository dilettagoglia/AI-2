# karen1 = karen('karen1')
# res1 = karen1.createGame(x)
# res1 = karen1.joinGame(x)
# res1 = karen1.startGame()

# karen2 = karen('karen2')
# res2 = karen2.joinGame(x)
# res2 = karen2.startGame()
# dichiaro che sono pronto con START. Il server risponde OK solo quando il gioco inizia effettivamente
# a questo punto inizia la mia strategia karen1.strategy()

from karen import Karen
gameName = "555"
myname = "imnotowner"
karen1 = Karen("amIowner")
karen2 = Karen(myname)

karen1.createGame(gameName)
karen1.joinGame(gameName, "amIowner", "AI", "-")
karen2.joinGame(gameName, myname, "AI", "-")

karen1.lookStatus()
karen1.startGame()
karen1.lookStatus()
karen1.strategy()
karen1.leaveGame()
