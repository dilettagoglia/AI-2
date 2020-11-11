import random

class movement():

    def __init__(self, param):
        #set eventuali parametri
        self.param = param



class rand_movement(movement):

    def __init__(self, param=None):
        #set eventuali parametri, passa alla classe super quelli di sua competenza
        movement.__init__(self, param)

    def move(self):
        possibility = ["N", "S", "W", "E"]
        direction = random.choice(possibility)
        return str(direction)


class rb_movement(movement):

    def __init__(self, param):
        #set eventuali parametri, passa alla classe super quelli di sua competenza
        movement.__init__(self, param)

