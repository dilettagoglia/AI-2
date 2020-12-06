import telnetlib

import time


# Driver per la connessione tra Server e il nostro sistema. Resta in esecuzione mantenendo la connessione con il server.
# Internamente offrirà una socket per leggere e scrivere

class connectToServer(object):
    """
    Diver used for the connection with the server.
    """
    net = None
    internalSocket = None

    def __init__(self, host, port, delay):
        """
        Open the connection with the server.
        :param host: define the host server name.
        :param port: define the port.
        :param delay: define the delay time
        """
        self.HOST = host
        self.port = port
        self.delay = float(delay)
        try:
            self.net = telnetlib.Telnet(self.HOST, self.port)
            self.ts = time.time()
        except:
            print("Connection Error")
            return

    def send(self, command):
        """
        Send a string to the server. Wait a prefixed delay checking the difference between the last 'send' timestamp with the new one
        :param command: define the command to send to the server.
        :return: the response from server.
        """
        response = []

        if abs(self.ts - time.time()) <= float(self.delay):
            time.sleep(float(self.delay) - abs(self.ts - time.time()))

        self.net.write(command.encode('utf-8') + b"\n")


        response = [text.strip() for text in self.net.read_until(b"\n").decode('utf-8').splitlines()]
        self.ts = time.time()

        # if(response[0] == "ERROR 401 Too fast"):
        #    per ora non usato perchè if True Jarvis ci chiude la socket
        #    return self.send(command)

        if response[0] == "OK LONG":
            nextField = ""
            while nextField != "«ENDOFSTATUS»" and nextField != "«ENDOFMAP»":

                nextField = self.net.read_until(b"\n").decode('utf-8').rstrip()
                response.append((nextField))


        return response
