import socket
from threading import Thread, Lock, RLock
import time
from datetime import *

from data_structure import gameStatus


class ReceiveThread(Thread):
    """
    Define a listener thread that wait for chat messages.
    """
    def __init__(self, name, conn, tmp):
        """
        Set the basic thread parameters.
        :param name: the thread name.
        :param conn: the socket
        """
        Thread.__init__(self)
        self.conn = conn
        self.name = name
        self.plname = tmp

    def run(self):
        while (True):
            received = self.conn.recv(4096)
            #ts = time.time()
            dateTimeObj = datetime.now()
            timeObj = dateTimeObj.time()
            received = received.decode('utf-8')
            if received == '':
                break
            print('Sono ' + self.plname + ', Ricevuto: ' + received)
            pair = (received, timeObj)
            gameStatus.sharedList.append(pair)


class ConnectToChat(object):
    """
    Diver used for the connection with the chat system.
    """
    net = None
    received = None
    res = None
    bootstrap = None

    def __init__(self, host, port, name):
        """
        Open the connection with the chat system.
        :param host: define the remote hostName.
        :param port: define the port.
        :param name: define the "player"/"chatMember" name.
        """
        self.HOST = socket.gethostbyname(host)
        self.port = port
        self.bootstrap = "NAME " + name + '\n'

        try:
            self.net = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.net.connect((self.HOST, int(self.port)))
            tmp = self.net.send(str.encode(self.bootstrap))
            # print("Connected to the chatServer.")
        except:
            print("Connection Error \n")
            return
        # JOIN the Global Channel for communication from the Server.
        message = "JOIN " + "#GLOBAL" + "\n"
        self.net.send(str.encode(message))

        message = "JOIN " + "#LEAGUE" + "\n"
        self.net.send(str.encode(message))

    def connectToChannel(self, game):
        """
        Send a connection request for a specific channel.
        :param game: the channel/game name.
        :return: None
        """
        message = "JOIN " + game + "\n"
        try:
            tmp2 = self.net.send(str.encode(message))
        except:
            print("Connection lost... \n")
            return

    def leaveChannel(self, game):
        """
        Send a leave request for a specific channel.
        :param game: the channel/game name.
        :return: None
        """
        message = "LEAVE " + game + '\n'
        try:
            self.net.send(str.encode(message))
        except:
            print("Connection lost... \n")
            return
        # print('Left: ' + message + '\n')

    def sendInChat(self, game, message):
        """
        Send a message in a chat.
        :param game: the channel name where to send a message.
        :param message: the message to be sent
        :return: None
        """
        send_msg = "POST " + game + " " + message + "\n"
        # print(send_msg)
        self.net.sendall(str.encode(send_msg))
        # print('inviato \n')
