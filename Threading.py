from threading import Thread


# inutile per ora
class SendThread (Thread):
    def __init__(self, conn, game, msg):
        Thread.__init__(self)
        self.conn = conn
        self.game = game
        self.mess = msg

    def run(self):
        #print ("Thread '" + self.name + "' avviato \n")
        self.conn.sendInChat(self.game, self.mess)
        #print ("Thread '" + self.name + "' terminato \n")


class ReceiveThread (Thread):
    def __init__(self, name, conn):
        Thread.__init__(self)
        self.conn = conn
        self.name = name

    def run(self):
        print ("Thread '" + self.name + "' avviato \n")
        while(True):
            received = self.conn.recv(4096)
            received = received.decode('utf-8')
            if received == '':
                break
            msg_toprint = "Received: " + received
            print(msg_toprint)


