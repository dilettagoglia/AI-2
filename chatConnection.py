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
        self.bootstrap = "NAME " + name

        try:
            self.net = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.net.connect((self.HOST, int(self.port)))
            print("Connected \n")

            self.net.sendall(str.encode(self.bootstrap))
            print("Nome inviato: " + self.bootstrap + '\n')

        except:
            print("Connection Error \n")
            return

    def connectToChannel(self, game):
        message = "JOIN " + game
        message2 = "JOIN " + "#GLOBAL"
        print(str.encode(message))

        try:
            self.net.sendall(str.encode(message))
            self.net.sendall(str.encode(message2))

        except:
            print("Connection lost... \n")
            return

        print('Joinato: ' + message + '\n')
        print('Joinato: ' + message2 + '\n')
        print(self.net)
        t_r = ReceiveThread('Receive', self.net)
        t_r.start()

    def leaveChannel(self, game):
        message = "LEAVE " + game

        try:
            self.net.send(str.encode(message))

        except:
            print("Connection lost... \n")
            return

        print('Left: ' + message + '\n')

    def sendInChat (self, game, message):
        send_msg = "POST " + game + " " + message
        print(send_msg)
        self.net.sendall(str.encode(send_msg))
        print('inviato \n')





