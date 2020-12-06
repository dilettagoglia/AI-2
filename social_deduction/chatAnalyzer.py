from threading import Thread
import re
from data_structure.socialDedDB import *
from data_structure.gameStatus import *
from data_structure import gameStatus
import time


class ChatAnalysisThread(Thread):
    def __init__(self, name):
        Thread.__init__(self)
        self.name = name
        # copio tutti i player nel db per la social ded
        for i in gameStatus.game.enemies.keys():
            name = gameStatus.game.enemies.get(i).name
            team = gameStatus.game.enemies.get(i).team
            pl = SD_Player(name, team)
            gameStatus.db.playerList[name] = pl
        for i in gameStatus.game.allies.keys():
            name = gameStatus.game.allies.get(i).name
            team = gameStatus.game.allies.get(i).team
            pl = SD_Player(name, team)
            gameStatus.db.playerList[name] = pl

    def run(self):
        while True:
            if len(gameStatus.sharedList) > 0:
                received = gameStatus.sharedList.pop()  # è coppia stringa timestamp
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
                            gameStatus.game.state = 'ACTIVE'
                        if tmp[2] == 'Game':
                            gameStatus.game.state = 'FINISHED'
                        if tmp[2] == 'Hunting':
                            gameStatus.game.stage = 1
                            # 654324 @GameServer Hunting season open!
                        if tmp[2] == 'You':
                            gameStatus.game.stage = 2
                            # 104223 @GameServer You can now catch the flag!
                        if tmp[3] == 'hit':
                            # 654324 @GameServer pinko2 hit pinko
                            # aggiungo pinko a lista killed di pinko2
                            if gameStatus.db.playerList.get(tmp[2]) is None:
                                trovato = 0
                                team = None
                                for i in gameStatus.game.enemies.keys():
                                    if gameStatus.game.enemies.get(i).name == tmp[2]:
                                        team = gameStatus.game.enemies.get(i).team
                                        trovato = 1
                                        break
                                if trovato == 0:
                                    for i in gameStatus.game.allies.keys():
                                        if gameStatus.game.allies.get(i).name == tmp[2]:
                                            team = gameStatus.game.allies.get(i).team
                                            break
                                pl = SD_Player(tmp[2], team)
                                gameStatus.db.playerList[tmp[2]] = pl  # aggiungi chiave al dizionario
                            gameStatus.db.playerList.get(tmp[2]).kills.append((tmp[4], received_time))

                            trovato1 = 0
                            for i in gameStatus.game.enemies.keys():
                                # scorri per trovare quello con lo stesso nome
                                if gameStatus.game.enemies.get(i).name == tmp[4]:
                                    gameStatus.game.enemies.get(i).state = 'KILLED'
                                    trovato1 = 1
                            if trovato1 == 0:
                                for i in gameStatus.game.allies.keys():
                                    # scorri per trovare quello con lo stesso nome
                                    if gameStatus.game.allies.get(i).name == tmp[4]:
                                        gameStatus.game.allies.get(i).state = 'KILLED'
                            # aggiorna status del giocatore ucciso in MORTO

                    else:
                        # messaggi player
                        if gameStatus.db.playerList.get(tmp[1]) is None:
                            trovato = 0
                            team = None
                            for i in gameStatus.game.enemies.keys():
                                if gameStatus.game.enemies.get(i).name == tmp[1]:
                                    team = gameStatus.game.enemies.get(i).team
                                    trovato = 1
                                    break
                            if trovato == 0:
                                for i in gameStatus.game.allies.keys():
                                    if gameStatus.game.allies.get(i).name == tmp[1]:
                                        team = gameStatus.game.allies.get(i).team
                                        trovato = 1
                                        break
                            pl = SD_Player(tmp[1], team)
                            gameStatus.db.playerList[tmp[1]] = pl  # aggiungi chiave al dizionario
                        # cerco nel decisionDB il player corrispondente e aggiungo alla lista di messaggi inviati il messaggio
                        gameStatus.db.playerList.get(tmp[1]).messages.append((received_str, received_time))
                        #for i in gameStatus.db.playerList:
                            #print(gameStatus.db.playerList.get(i).messages)


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
            # controlla che abbia ucciso compagni di squadra
            for i in gameStatus.db.playerList.keys():
                for j in gameStatus.db.playerList.get(i).kills:
                    j_name = gameStatus.db.playerList.get(i).kills[j][0]
                    j_time = gameStatus.db.playerList.get(i).kills[j][1]
                    if gameStatus.db.playerList.get(i).team is not None and gameStatus.db.playerList.get(j_name).team is not None:
                        if gameStatus.db.playerList.get(i).team == gameStatus.db.playerList.get(j_name).team:
                            gameStatus.db.playerList.get(i).sdScore += 0.2

            # altre cose poi
            #startvote (poi)
            #if gameStatus.db.playerList.get(i).sdScore > 0.8:
             #   None
                # setta un flag globale che dice a karen se votare?
                # karen a ogni iter controlla la variabile e se c'è qualcosa fa la votazione





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
            time.sleep(5)
            count = 0
            for i in gameStatus.db.playerList.keys():
                for j in gameStatus.db.playerList.get(i).messages:
                    for z in gameStatus.db.playerList.get(i).messages:
                        if j[0] == z[0] & j[1] != z[1]:
                            count = count + 1
                            gameStatus.db.playerList.get(i).turingScore += 0.1
                if count <= len(gameStatus.db.playerList.get(i).messages):
                    gameStatus.db.playerList.get(i).turingScore -= 0.1

                if gameStatus.db.playerList.get(i).turingScore > 0.8:
                    None
                    # setta un flag globale che dice a karen se votare?
                    # karen a ogni iter controlla la variabile e se c'è qualcosa fa la votazione

                if gameStatus.db.playerList.get(i).turingScore < 0.2:
                    None
                    # setta un flag globale che dice a karen se votare?
