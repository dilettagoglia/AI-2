import telnetlib

class connectToServer(object):

    def __init__(self):
        print("inside __init__ of Tel class")
        self.HOST = "margot.di.unipi.it"
        self.port = "8421"
        self.net = telnetlib.Telnet(self.HOST, self.port)
        print("Connected")

    def sendcmd(self, command):
        self.net.write(command.encode('utf-8') + b"\n")
        response = [text.strip() for text in self.net.read_until(b")", 10).decode('utf-8').splitlines()]
        return response

ne_obj = connectToServer()
cmdoutput = ne_obj.sendcmd("test LOOK")
print(cmdoutput)