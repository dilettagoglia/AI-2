import configparser
from connection.chatConnection import ConnectToChat
#from Threading import SendThread
import time


class Karen(object):

    def __init__(self, name):
        self.name = name
        print("I am " + self.name)

        config = configparser.ConfigParser()
        config.read('config')

        self.host = config['chatParam']['HOST']
        self.port = config['chatParam']['PORT']

        self.conn = ConnectToChat(self.host, self.port, self.name)

    # inutile adesso
    #def sendMsg (self, game, msg):
    #    t1 = SendThread(self.conn, game, msg)
    #    t1.start()
        print('inviato')


k = Karen('GinoPippo')
k.conn.connectToChannel('aaa')

k2 = Karen('vfsdcaf')
k2.conn.connectToChannel('aaa')

time.sleep(3)
k.conn.sendInChat('aaa', 'primo')
k.conn.connectToChannel('bbb')

time.sleep(3)
k.conn.sendInChat('aaa', 'secondo')
k2.conn.sendInChat('bbb', 'primo2')




