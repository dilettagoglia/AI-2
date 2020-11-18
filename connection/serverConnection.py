import telnetlib


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
        self.delay = delay
        try:
            self.net = telnetlib.Telnet(self.HOST, self.port)
        except:
            print("Connection Error")
            return

    def send(self, command):
        """
        Send a string to the server.
        :param command: define the command to send to the server.
        :return: the response from server.
        """
        response = None
        self.net.write(command.encode('utf-8') + b"\n")

        while response is None or response is [] or response is "ERROR 401 Too fast":
            response=[]
            response = [text.strip() for text in self.net.read_until(b")", float(self.delay)).decode('utf-8').splitlines()]


        return response

