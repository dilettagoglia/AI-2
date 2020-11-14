from threading import Thread
import time
#from chatConnection import ConnectToChat


class SendThread (Thread):
    def __init__(self, conn, game, msg):
        Thread.__init__(self)
        self.conn = conn
        self.game = game
        self.mess = msg

    def run(self):
        print ("Thread '" + self.name + "' avviato \n")
        self.conn.sendInChat(self.game, self.mess)
        print ("Thread '" + self.name + "' terminato \n")


class ReceiveThread (Thread):
    def __init__(self, name, conn):
        Thread.__init__(self)
        self.conn = conn
        self.name = name

    def run(self):
        print ("Thread '" + self.name + "' avviato \n")
        #while(True):
        #self.conn.receiveChat()
        print('prima di receiv ' + str(self.conn))
        received = self.conn.recv(4096)
        print('dopo receive')
        received = received.decode('utf-8')
        msg_toprint = "Received: " + received
        print(msg_toprint)

