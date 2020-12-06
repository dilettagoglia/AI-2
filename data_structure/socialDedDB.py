class DecisionsDB:
    def __init__(self):
        self.playerList = dict()  # popolata come player. Inserito in game?


class SD_Player:
    def __init__(self, name, team):
        self.name = name
        self.team = team
        self.turingScore = 0.5
        self.sdScore = 0
        self.kills = []
        self.messages = []

'''
struttura decisions_db:
    lista di player_sd

struttura player_sd
	valore per impostore
	valore per turing
	lista coppie (nemici uccisi, timestamp)
	lista coppie (messaggio inviato, timestamp)

thread receiver prende messaggi ricevuti,
    ts = timestamp
    listacond.append (received, ts)

un thread a parte che cicla all'infinito
	if (lista condivisa != vuoto):
		pop primo elemento (coppia)
		analisi della stringa per vedere a quale player mettere
si avrà un dizionario
'''


