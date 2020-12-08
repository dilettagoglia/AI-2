from datetime import datetime
from threading import Thread
import re
from data_structure.socialDedDB import *
from data_structure.gameStatus import *
from data_structure import gameStatus
import time

from strategy.pathFinder import findPath


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
        #print('LISTA IN DB: ' + str(gameStatus.db.playerList))
    def run(self):
        while True:
            if len(gameStatus.sharedList) > 0:
                time.sleep(0.2)
                received = gameStatus.sharedList.pop()  # è coppia stringa timestamp
                received_str = received[0]
                received_time = received[1]
                #print('\n TIME: ' + str(received_time) + '\n')
                tmp = re.split(' |\n', received_str)
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
                        if tmp[2] == 'EMERGENCY':
                            if tmp[4] == 'Called':
                                gameStatus.game.emergencyMeeting = 1
                                # EM, fai votare karen
                            if tmp[4] == 'condamned':
                                # espulso da EM, metti a KILLED il suo stato
                                if gameStatus.game.me.name == tmp[5]:
                                    gameStatus.game.me.state = 'KILLED'
                                for i in gameStatus.game.allies.keys():
                                    ############### contollo che non sia io
                                    # scorri per trovare quello con lo stesso nome
                                    if gameStatus.game.allies.get(i).name == tmp[5]:
                                        gameStatus.game.allies.get(i).state = 'KILLED'
                                        break
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
                            if gameStatus.game.me.name == tmp[4]:
                                gameStatus.game.me.state = 'KILLED'
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
            for i in db.playerList.get(j).messages:
                        if (i contien qualcosa come 'non sono io' oppure 'sono innocente): (NLP)
                            incrementa punteggio di impostor
            if (passa vicino bandiera e non la prende | non uccide nemici quando li incrocia): (salvare percorso degli altri player?)
                incrementa punteggio di impostor
            for i in db.playerList.get(j).messages:
                if (i contien qualcosa come 'non sono io' oppure 'sono innocente): (NLP)
                    diminuisci punteggio di impostor (troppo credulone forse)
            '''
            # faccio aggiornamento ogni 5 secondi
            time.sleep(5)
            # controlla che abbia ucciso compagni di squadra
            for i in gameStatus.db.playerList.keys():
                #print('\n SD dentro for, ora farebbe cose \n')
                for j in range (0, len(gameStatus.db.playerList.get(i).kills)):
                    #print ('\n SD dentro seconndo for \n')
                    coppia = gameStatus.db.playerList.get(i).kills[j]
                    j_name = coppia[0]
                    j_time = coppia[1]
                    #print('\n SD coppia scorporata: ' + str(j_name) + '\n')
                    if gameStatus.db.playerList.get(i).team is not None and gameStatus.db.playerList.get(j_name).team is not None:
                        #print('\n SD dentro primo if \n')
                        if gameStatus.db.playerList.get(i).team == gameStatus.db.playerList.get(j_name).team:
                            #print('\n SD dentro secondo if \n')
                            gameStatus.db.playerList.get(i).sdScore += 0.2
                            #print ('\n GIRO DI SD COMPLETO: ' + str(gameStatus.db.playerList.get(i).sdScore))
                        #print('\n OK SEMBRO FUNZIONARE: ' +  str(gameStatus.db.playerList.get(i).sdScore) + '\n')

            # altre cose poi
            #startvote
                if gameStatus.db.playerList.get(i).sdScore > 0.8:
                    gameStatus.game.emergencyMeeting = 1


class TuringTestThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        datetimeFormat = '%H:%M:%S.%f'
        dt1 = datetime.now()
        t1 = dt1.time()
        while True:
            '''
            se scrive sempre messaggi corretti grammatcalmente:
                punteggio verso AI 
            se scrive messaggi sbagliati:
                punteggio verso HU           
            
            #faccio aggiornamento ogni 5 secondi
            time.sleep(5)
            for i in gameStatus.db.playerList.keys():
                # controllo che scriva più volte messaggi esattamente uguali
                count = 0
                for j in range (0, len(gameStatus.db.playerList.get(i).messages)):
                    for z in range (0, len(gameStatus.db.playerList.get(i).messages)):
                        if j[0] == z[0] & j[1] != z[1]:
                            count = count + 1
                            gameStatus.db.playerList.get(i).turingScore += 0.1
                if count <= len(gameStatus.db.playerList.get(i).messages): # incontrerà sempre almeno una volta sè stesso
                    # in tal caso tutti diversi
                    gameStatus.db.playerList.get(i).turingScore -= 0.1

                datetimeFormat = '%H:%M:%S.%f'
                # controllo che ci sia il tempo materiale per scrivere tra uccisione e messaggio eventuale in chat
                for j in range (0, len(gameStatus.db.playerList.get(i).kills)):
                    for z in range (0, len(gameStatus.db.playerList.get(i).messages)):
                        diff = datetime.datetime.strptime(z[1], datetimeFormat) - datetime.datetime.strptime(j[1], datetimeFormat)
                        if diff.seconds <= 1:
                            gameStatus.db.playerList.get(i).turingScore += 0.1

                #controllo che non scriva messaggi troppo vicini
                for j in range (0, len(gameStatus.db.playerList.get(i).messages)):
                    for z in range (0, len(gameStatus.db.playerList.get(i).messages)):
                        diff = datetime.datetime.strptime(z[1], datetimeFormat) - datetime.datetime.strptime(j[1], datetimeFormat)
                        if diff.seconds <= 1:
                            gameStatus.db.playerList.get(i).turingScore += 0.1

                #se non scrive mai nulla posso assumere che sia umano? troppo concentrato a giocare

                # JUDGE
                if gameStatus.db.playerList.get(i).turingScore > 0.8:
                    None
                    # setta un flag globale che dice a karen se votare?
                    # karen a ogni iter controlla la variabile e se c'è qualcosa fa la votazione

                if gameStatus.db.playerList.get(i).turingScore < 0.2:
                    None
                    # setta un flag globale che dice a karen se votare?
        '''
            # Cheating
            positions_enemies_before = gameStatus.game.enemies
            positions_allies_before = gameStatus.game.allies
            time.sleep(1) #AI possono fare al massimo 3 passi
            positions_enemies_after = gameStatus.game.enemies
            positions_allies_after = gameStatus.game.allies

            for i in positions_enemies_before.keys():
                name = positions_enemies_before.get(i).name
                if gameStatus.db.playerList.get(name).turingScore == 0:
                    continue
                else:
                    path = findPath(gameStatus.game.weightedMap, positions_enemies_before.get(i), positions_enemies_after.get(i).x, positions_enemies_after.get(i).y)
                    diff = len(path)
                    if diff > 3:
                        gameStatus.db.playerList.get(name).turingScore = 0
                        gameStatus.judgeList.append((name, 'H'))
                    else:
                        gameStatus.db.playerList.get(name).turingScore = 0.7

            gameStatus.db.playerList.get(gameStatus.game.me.name).turingScore = 1

            for i in positions_allies_before.keys():
                name = positions_allies_before.get(i).name
                if gameStatus.db.playerList.get(name).turingScore == 0:
                    continue
                else:
                    path = findPath(gameStatus.game.weightedMap, positions_allies_before.get(i), positions_allies_after.get(i).x, positions_allies_after.get(i).y)
                    diff = len(path)
                    if diff > 3:
                        gameStatus.db.playerList.get(name).turingScore = 0
                        gameStatus.judgeList.append((name, 'H'))
                    else:
                        gameStatus.db.playerList.get(name).turingScore = 0.7

            dt2 = datetime.now()
            t2 = dt2.time()
            diff = datetime.strptime(str(t2), datetimeFormat) - datetime.strptime(str(t1), datetimeFormat)
            if diff.seconds > 7:
                for i in gameStatus.db.playerList.keys():
                    if gameStatus.db.playerList.get(i).turingScore != 0:
                        gameStatus.db.playerList.get(i).turingScore = 1
                        gameStatus.judgeList.append((i, 'AI'))
                #print('HO FINITO \n')
                #for i in gameStatus.db.playerList.keys():
                 #   print('VALORE TURING: ' + str(gameStatus.db.playerList.get(i).turingScore) + '\n')
                #print('ADDIO MONDO CRUDELE \n')
                return
