import re
import sys
from os import listdir
from os.path import isfile, join

import pickle


class MlDatabase:
    def __init__(self):
        self.playerList = dict()  # chiave: nome, valore:lista (o struttura con liste di azioni e mappe (con timestamp))


class MlPlayer:
    def __init__(self, name):
        self.nome = name
        self.act_list = []  # tupla (x, y, azion, info (dist in polare o bersaglio shoot))
        self.team = None
        self.coord = None
        self.flagToCatch = None


mypath = r"C:\Users\Matteo\Desktop\Logbuoi"
all_files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
print('LUNGHEZZA FILES: ' + str(len(all_files)))
ml_database = MlDatabase()

previous_line = None
tmp_map = []
tmp_time = None
tmp_status = []
mpa = []
count = 0

for f in listdir(mypath):
    f2 = mypath + '/' + str(f)
    #print(f2)
    firstmap = True
    fiststatus = True
    checkstatus = False
    coord_flag_min = None
    coord_flag_max = None
    with open(f2, "r") as file:
        for line in file:
            # print(('nuova riga'))
            tmp = re.split(' |\n', line)
            # print(tmp)

            # mappa
            if firstmap == True:
                if previous_line is not None:
                    if len(previous_line[0]) > 30 and len(tmp[0]) < 10:
                        mpa.append(tmp_map)
                        # print('sto qua')
                        # salva coordinate
                        for i in range(len(tmp_map)):
                            for j in range (len(tmp_map[0])):
                                #print (str(i) + ' ' + str(j))

                                #print('STAMPOOOO')
                                #print(tmp_map[i][j])
                                if tmp_map[i][j] == 'x':
                                    #print('TROVATOOO piccolo:')
                                    #print(i, j)
                                    coord_flag_min = (i,j)
                                if tmp_map[i][j] == 'X':
                                    #print('TROVATOOO grande:')
                                    #print(i, j)
                                    coord_flag_max = (i, j)
                        tmp_map = []
                        firstmap = False
                if len(tmp[0]) > 30:
                    # print('sono qui')
                    # print("T'HO CIOCCATO: " + tmp[0] + "\n")
                    tmp_map.append(tmp[0])

            # status
            if fiststatus == True:
                if previous_line is not None:
                    if previous_line[1].startswith('symbol=') and not tmp[1].startswith('symbol='):
                        #associo team a player
                        tmp_status = []
                        if checkstatus == True:
                            fiststatus = False
                if tmp[1].startswith('symbol=') or tmp[1].startswith('name='):
                    if tmp[0].startswith('PL'):
                        tmp_status.append(tmp)
                        tosplitname = tmp[2]
                        tosplitname = re.split('=', tosplitname)
                        sname = tosplitname[1]
                        nome = f2 + str(sname)
                        #print(nome)
                        tosplitteam = tmp[3]
                        tosplitteam = re.split('=', tosplitteam)
                        tteam = tosplitteam[1]
                        tosplitx = tmp[4]
                        tosplitx = re.split('=', tosplitx)
                        tosplity = tmp[5]
                        tosplity = re.split('=', tosplity)
                        coord = (tosplitx[1], tosplity[1])
                        if ml_database.playerList.get(nome) is not None:
                            ml_database.playerList.get(nome).team = tteam
                            ml_database.playerList.get(nome).coord = coord
                            if tteam == 0:
                                ml_database.playerList.get(nome).flagToCatch = coord_flag_min
                            else:
                                ml_database.playerList.get(nome).flagToCatch = coord_flag_max
                    if tmp[0].startswith('GA'):
                        tosplitlobby = tmp[2]
                        tosplitlobby = re.split('=', tosplitlobby)
                        if tosplitlobby[1] == 'ACTIVE':
                            checkstatus = True

            # parte dei player in cui salvo azioni
            if len(tmp) > 4:
                if tmp[2] != 'STATUS' and tmp[2] != 'MAP' and tmp[2] != 'PLAYER-DISCONNECTED' and tmp[2] != 'SCORES' and tmp[2] != 'VICTORY':
                    if not tmp[1].startswith('name') and not tmp[1].startswith('symbol'):
                        if len(tmp[0]) < 30:
                            #nome = tmp[2]
                            nome = f2 + str(tmp[2])
                            #print(nome)
                            if ml_database.playerList.get(nome) is None:
                                pl = MlPlayer(nome)
                                ml_database.playerList[nome] = pl
                            act = tmp[3]
                            if checkstatus == True:
                                if act == 'MOVE' or act == 'SHOOT':
                                    direction = tmp[4]
                                    res = tmp[5]
                                    if tmp[5] == 'res_not_found':
                                        to_save = (act, direction, res, tmp[5])
                                    else:
                                        res2 = tmp[6]

                                        if act == 'MOVE':
                                            if tmp[6] == 'moved':
                                                #print(tmp[6])
                                                ncoord = ml_database.playerList.get(nome).coord
                                                #print(ncoord)
                                                #print (nome)
                                                if direction == 'N':
                                                    ncoord = (ncoord[0], int(ncoord[1]) - 1)
                                                    to_save = (act, direction, res, res2, ncoord)
                                                    ml_database.playerList.get(nome).coord = ncoord
                                                elif direction == 'S':
                                                    ncoord = (ncoord[0], int(ncoord[1]) + 1)
                                                    to_save = (act, direction, res, res2, ncoord)
                                                    ml_database.playerList.get(nome).coord = ncoord
                                                elif direction == 'E':
                                                    ncoord = (int(ncoord[0]) + 1, int(ncoord[1]))
                                                    to_save = (act, direction, res, res2, ncoord)
                                                    ml_database.playerList.get(nome).coord = ncoord
                                                else:
                                                    ncoord = (int(ncoord[0]) - 1, int(ncoord[1]))
                                                    to_save = (act, direction, res, res2, ncoord)
                                                    ml_database.playerList.get(nome).coord = ncoord
                                        else:
                                            ncoord = ml_database.playerList.get(nome).coord
                                            to_save = (act, direction, res, res2, ncoord)

                                else:
                                    to_save = (act, None)
                                ml_database.playerList.get(nome).act_list.append(to_save)
                                # ml_database.playerList.get(nome).act_list.append(line)

            previous_line = tmp

#print('mappe ottenute: ' + str(len(mpa)))
#print(ml_database.playerList)
#print(ml_database.playerList.get('C:\\Users\Matteo\Desktop\loggi/2020-12-09--17-55-02.txtCannellone').act_list)
print(ml_database.playerList.get('C:\\Users\Matteo\Desktop\Logbuoi/2020-12-09--17-55-02.txtCannellone').act_list)

with open('dati_salvati.pickle', 'wb') as handle:
    pickle.dump(ml_database, handle, protocol=pickle.HIGHEST_PROTOCOL)