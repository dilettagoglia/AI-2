import random
from pathFinder import *

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
        # set eventuali parametri, passa alla classe super quelli di sua competenza
        movement.__init__(self, param)

    def move(self,  actualMap=None, startx=None, starty=None, endx=None, endy=None):

        coordinate = findPath(actualMap, startx, starty, endx, endy)

        # x: spostamento all'interno di una lista
        # y: spostamento da una lista all'altra

        if startx > coordinate[0]:
            direction = "W"
        elif startx < coordinate[0]:
            direction = "E"
        else:
            if starty > coordinate[1]:
                direction = "N"
            elif starty < coordinate[1]:
                direction = "S"

        return direction