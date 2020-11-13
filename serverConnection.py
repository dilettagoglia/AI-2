import telnetlib

#Driver per la connessione tra Server e il nostro sistema. Resta in esecuzione mantenendo la connessione con il server.
#Internamente offrirà una socket per leggere e scrivere

#  AI Module  <-socket interna->  connectToServer  <-client telnet->

class connectToServer(object):
    net = None
    internalSocket = None


    def __init__(self, host, port):
        self.HOST = host
        self.port = port
        try:
            self.net = telnetlib.Telnet(self.HOST, self.port)
        except:
            print("Connection Error")
            return


    def send(self, command):
        self.net.write(command.encode('utf-8') + b"\n")
        response = [text.strip() for text in self.net.read_until(b")", 10).decode('utf-8').splitlines()]
        return response


#ne_obj = connectToServer()
#cmdoutput = ne_obj.send("test LOOK")
#print(cmdoutput)