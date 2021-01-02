from threading import Thread


class gameAnalyzer(Thread):
    def __init__(self, name):
        Thread.__init__(self)
        self.name = name

    def run(self):

        while True:
            None
