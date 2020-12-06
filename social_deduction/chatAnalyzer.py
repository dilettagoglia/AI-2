from threading import Thread
import re
from data_structure.socialDedDB import *
from data_structure.gameStatus import *
from data_structure import gameStatus

class ChatAnalysisThread(Thread):
    def __init__(self, name):
        Thread.__init__(self)
        self.name = name
        #global db
        #global sharedList
        #sharedList = lista
        #db = database

    def run(self):
        while True:
            if len(gameStatus.sharedList) > 0:
                gameStatus.mutex_sl.acquire()
                received = gameStatus.sharedList.pop()  # è coppia stringa timestamp
                gameStatus.mutex_sl.release()
                received_str = received[0]
                received_time = received[1]
                # print("dentro thread hestore: " + received_str)
                tmp = re.split(' |\n', received_str)
                #print(gameStatus.game.enemies)
                if tmp[0] == '#GLOBAL':
                    if tmp[1] == '@GameServer':
                        None
                        # notifiche di sistema
                else:
                    if tmp[1] == '@GameServer':
                        # notifiche del server relative alla partita
                        if tmp[2] == 'Now':
                            gameStatus.mutex_ga.acquire()
                            #print("PRIMA di aggiornamento: " + str(gameStatus.game.state))
                            gameStatus.game.state = 'ACTIVE'
                            #print('Paritta iniziata: ' + str(gameStatus.game.state))
                            gameStatus.mutex_ga.release()
                        if tmp[2] == 'Game':
                            gameStatus.mutex_ga.acquire()
                            #print("PRIMA di aggiornamento: " + str(gameStatus.game.state))
                            gameStatus.game.state = 'FINISHED'
                            #print('PArtita dinita : ' + str(gameStatus.game.state))
                            gameStatus.mutex_ga.release()
                        if tmp[2] == 'Hunting':
                            gameStatus.mutex_ga.acquire()
                            #print("PRIMA di aggiornamento: " + str(gameStatus.game.stage) )
                            gameStatus.game.stage = 1
                            #print('PASSATI 7 secondi: ' + str(gameStatus.game.stage))
                            gameStatus.mutex_ga.release()
                            # 654324 @GameServer Hunting season open!
                        if tmp[2] == 'You':
                            gameStatus.mutex_ga.acquire()
                            gameStatus.game.stage = 2
                            #print('PASSATI 7 secondi: ' + str(gameStatus.game.stage))
                            gameStatus.mutex_ga.release()
                            # 104223 @GameServer You can now catch the flag!
                        if tmp[3] == 'hit':
                            # 654324 @GameServer pinko2 hit pinko
                            # aggiungo W a lista killed di pinko2
                            gameStatus.mutex_db.acquire()
                            if gameStatus.db.playerList.get(tmp[2]) is None:
                                pl = SD_Player(tmp[2])
                                gameStatus.db.playerList[tmp[2]] = pl  # aggiungi chiave al dizionario
                            gameStatus.db.playerList.get(tmp[2]).kills.append((tmp[4], received_time))
                            gameStatus.mutex_db.release()

                            trovato = 0
                            gameStatus.mutex_ga.acquire()
                            #print('nemici presenti: ' + gameStatus.game.enemies + '\n')
                            #print('nome nemico: ' + gameStatus.game.enemies.get('a').name + '\n')
                            #if tmp[4] in gameStatus.game.enemies:
                            for i in gameStatus.game.enemies.keys():
                                # scorri per trovare quello con lo stesso nome
                                if gameStatus.game.enemies.get(i).name == tmp[4]:
                                    gameStatus.game.enemies.get(i).state = 'KILLED'
                                    #print('MORTOOOO ' + gameStatus.game.enemies.get(i).state + '\n')
                                    trovato = 1
                            if trovato == 0:
                                for i in gameStatus.game.allies.keys():
                                    # scorri per trovare quello con lo stesso nome
                                    if gameStatus.game.allies.get(i).name == tmp[4]:
                                        gameStatus.game.allies.get(i).state = 'KILLED'
                                        #print('MORTOOOO ' + gameStatus.game.allies.get(i).state + '\n')
                                        trovato = 1
                            # aggiorna status del giocatore ucciso in MORTO
                            gameStatus.mutex_ga.release()

                    else:
                        # messaggi player
                        gameStatus.mutex_db.acquire()
                        if gameStatus.db.playerList.get(tmp[1]) is None:
                            pl = SD_Player(tmp[1])
                            gameStatus.db.playerList[tmp[1]] = pl  # aggiungi chiave al dizionario
                        # cerco nel decisionDB il player corrispondente e aggiungo alla lista di messaggi inviati il messaggio
                        gameStatus.db.playerList.get(tmp[1]).messages.append((received_str, received_time))
                        #for i in gameStatus.db.playerList:
                            #print(gameStatus.db.playerList.get(i).messages)
                        gameStatus.mutex_db.release()


# spawnati in creazione di karen
class SocialDeductionThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        while True:
            '''
            # finchè non NN:
            for j in range (0, len(db.playerList)):
                for i in db.playerList.get(j).kills:
                    if (player con stesso nome è in game.allies):
                        if (player_ucciso è in game.allies):
                            incrementa punteggio di impostor
                        for i in db.playerList.get(j).messages:
                            if (i contien qualcosa come 'non sono io' oppure 'sono innocente): (NLP)
                                incrementa punteggio di impostor
                if (passa vicino bandiera e non la prende | non uccide nemici quando li incrocia): (salvare percorso degli altri player?)
                    incrementa punteggio di impostor
                for i in db.playerList.get(j).messages:
                    if (i contien qualcosa come 'non sono io' oppure 'sono innocente): (NLP)
                        diminuisci punteggio di impostor (troppo credulone forse)
            
            if (punteggio impostore > 0.8):
                avvia un voto
                vota quello con punteggio più alto
            '''
            None


class TuringTestThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        while True:
            '''
            # finchè non NN
            controlla che timestamp di uccisione ed eventuale messaggio in chat siano molto vicini:
                punteggio verso AI
            se scrive più volte messaggi uguali:
                punteggio verso AI 
            se scrive sempre messaggi corretti grammatcalmente:
                punteggio verso AI 
            se scrive messaggi sempre diversi:
                punteggio verso HU
            se scrive messaggi sbagliati:
                punteggio verso HU
                
            if (turingScore) > 0.8:
                metti che è HU:
            if (turingScore) < 0.2:
                metti che è AI
            '''
            None
