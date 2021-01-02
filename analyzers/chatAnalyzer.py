from datetime import datetime
from threading import Thread
import re
from data_structure import gameStatus



def chatAnalysis():
    received = gameStatus.sharedList.pop()  # è coppia stringa timestamp
    received_str = received[0]
    received_time = received[1]
    # print('\n TIME: ' + str(received_time) + '\n')
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
                        if gameStatus.game.allies.get(i).name == tmp[5]:
                            gameStatus.game.allies.get(i).state = 'KILLED'
                            break
                    for i in gameStatus.game.enemies.keys():
                        if gameStatus.game.enemies.get(i).name == tmp[5]:
                            gameStatus.game.enemies.get(i).state = 'KILLED'

                            break

            if tmp[3] == 'hit':
                # 654324 @GameServer pinko2 hit pinko
                # aggiungo pinko a lista killed di pinko2

                if gameStatus.game.allies.get(tmp[2]) is not None:
                    gameStatus.game.allies.get(tmp[2]).kills.append((tmp[4], received_time))

                elif gameStatus.game.enemies.get(tmp[2]) is not None:
                    gameStatus.game.enemies.get(tmp[2]).kills.append((tmp[4], received_time))

                if gameStatus.game.me.name == tmp[4]:
                    gameStatus.game.me.state = 'KILLED'

                for i in gameStatus.game.allies.keys():
                    if gameStatus.game.allies.get(i).name == tmp[4]:
                        gameStatus.game.allies.get(i).state = 'KILLED'

                        break
                for i in gameStatus.game.enemies.keys():
                    if gameStatus.game.enemies.get(i).name == tmp[4]:
                        gameStatus.game.enemies.get(i).state = 'KILLED'

                        break
                # aggiorna status del giocatore ucciso in MORTO

        else:
            # messaggi player
            if gameStatus.game.allies.get(tmp[1]) is not None:
                gameStatus.game.allies.get(tmp[1]).messages.append((received_str, received_time))
            elif gameStatus.game.enemies.get(tmp[1]) is not None:
                gameStatus.game.enemies.get(tmp[1]).messages.append((received_str, received_time))

            # for i in gameStatus.db.playerList:
            # print(gameStatus.db.playerList.get(i).messages)



class chatAnalyzer(Thread):
    def __init__(self, name):
        Thread.__init__(self)
        self.name = name

    def run(self):
        dt1 = datetime.now()
        t1 = dt1.time()
        while True:

            # If something arrives in chat, analyze it
            if len(gameStatus.sharedList) > 0:
                chatAnalysis()
