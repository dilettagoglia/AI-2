import socket
from Threading import *


class ConnectToChat(object):
    net = None
    received = None
    res = None
    bootstrap = None

    def __init__(self, host, port, name):
        self.HOST = socket.gethostbyname(host)
        self.port = port
        self.bootstrap = "NAME " + name + '\n'

        try:
            self.net = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.net.connect((self.HOST, int(self.port)))
            print("Connected \n")
            tmp = self.net.send(str.encode(self.bootstrap))

        except:
            print("Connection Error \n")
            return

        t_r = ReceiveThread('Receive', self.net)
        t_r.start()
        message = "JOIN " + "#GLOBAL" + "\n"
        self.net.send(str.encode(message))

    def connectToChannel(self, game):
        message = "JOIN " + game + "\n"
        try:
            tmp2 = self.net.send(str.encode(message))
        except:
            print("Connection lost... \n")
            return

    def leaveChannel(self, game):
        message = "LEAVE " + game + '\n'
        try:
            self.net.send(str.encode(message))

        except:
            print("Connection lost... \n")
            return
        # print('Left: ' + message + '\n')

    def sendInChat (self, game, message):
        send_msg = "POST " + game + " " + message + "\n"
        #print(send_msg)
        self.net.sendall(str.encode(send_msg))
        #print('inviato \n')





