from threading import Thread
import re
from data_structure.socialDedDB import *


class ChatAnalysisThread(Thread):
    def __init__(self, name, lista, database):
        Thread.__init__(self)
        self.name = name
        global db
        global sharedList
        sharedList = lista
        db = database

    def run(self):
        while True:
            if len(sharedList) > 0:
                received = sharedList.pop()  # è coppia stringa timestamp
                received_str = received[0]
                received_time = received[1]
                # print("dentro thread hestore: " + received_str)
                tmp = re.split(' |\n', received_str)
                if tmp[0] == '#GLOBAL':
                    if tmp[1] == '@GameServer':
                        None
                        # notifiche di sistema
                else:
                    if tmp[1] == '@GameServer':
                        # notifiche del server relative alla partita
                        if tmp[2] == 'Hunting':
                            None
                            # 654324 @GameServer Hunting season open!
                            # setto flag spari
                        if tmp[2] == 'You':
                            None
                            # 104223 @GameServer You can now catch the flag!
                            # setta flag per bandiera
                        if tmp[3] == 'shot':
                            None
                            # 654324 @GameServer pinko2 shot W
                            # aggiungo W a lista killed di pinko2
                            if db.playerList.get(tmp[2]) is None:
                                pl = SD_Player(tmp[2])
                                db.playerList[tmp[2]] = pl  # aggiungi chiave al dizionario
                            # elif db.playerList(tmp[2]) is not None:
                            db.playerList.get(tmp[2]).kills.append((tmp[4], received_time))
                            # print('Uccisioni: ' + str(db.playerList.get(tmp[2]).kills))
                            # aggiorna status del giocatore ucciso in MORTO
                        # inserire controlli su stato partita (ACTIVE, LOBBY, ENDED)

                    else:
                        # messaggi player
                        if db.playerList.get(tmp[1]) is None:
                            pl = SD_Player(tmp[1])
                            db.playerList[tmp[1]] = pl  # aggiungi chiave al dizionario
                            # print('creo chiave \n')
                        # elif db.playerList(tmp[2]) is not None:
                        db.playerList.get(tmp[1]).messages.append((received_str, received_time))
                        # print('Messaggi salvati di ' + self.name + ': ' + str(db.playerList.get(tmp[1]).messages))
                        # cerco nel decisionDB il player corrispondente e aggiungo alla lista di messaggi inviati il messaggio
                        for i in db.playerList:
                            print(db.playerList.get(i).messages)


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
