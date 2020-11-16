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

    def move(self,  actualMap, player, game, endx, endy):

        coordinate = findPath(actualMap, player, game, endx, endy)

        # x: spostamento all'interno di una lista
        # y: spostamento da una lista all'altra

        if player.x > coordinate[0]:
            direction = "W"
        elif player.x < coordinate[0]:
            direction = "E"
        else:
            if player.y > coordinate[1]:
                direction = "N"
            elif player.y < coordinate[1]:
                direction = "S"

        return direction