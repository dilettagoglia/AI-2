import configparser
from strategy.movement import *
from connection.serverConnection import *
from data_structure.gameStatus import *
from connection.chatConnection import *
import re
from strategy.fuzzyStrategy import *
from strategy.lowLevelStrategy import *
from strategy.deterministicMap import *
from multiprocessing import Process
from karentest import *

def f1(name):
    k2 = Karen('Pina', 'tmp')
    k2.chatSocket.connectToChannel('Test')
    time.sleep(2)
    k2.chatSocket.sendInChat('Test', 'Primo messaggio secondo processo')

def f(name):
    k = Karen('Ginopippo', 'tmp')
    k.chatSocket.connectToChannel('Test')
    time.sleep(2)
    k.chatSocket.sendInChat('Test', "Primo messaggio primo processo")

    #print ('processo partito \n')

if __name__ == '__main__':
    p = Process(target=f, args=('bob',))
    p1 = Process (target=f1, args=('mary',))
    p.start()
    p1.start()
   # p.join()


#k = Karen('Ginopippo', 'tmp')
#k2 = Karen('pina', 'tmp')
#k.chatSocket.connectToChannel('Test')
#k2.chatSocket.connectToChannel('Test')
#time.sleep(2)

#k.chatSocket.sendInChat('Test', "Primo messaggio")
#time.sleep(2)
#print ("Dopo messaggio " + str(len(sharedList)))
#k.chatSocket.sendInChat('Test', "Secondo messaggio")
#time.sleep(2)
#print ("Dopo messaggio2 " + str(len(sharedList)))
#print('len lista cond alla fine : ' + str(len(sharedList)))