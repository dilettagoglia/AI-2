import random
from strategy.pathFinder import *


# The idea of using class for movement came out to standardize the code in Karen.
class movement:
    """
    Parent "movement" class. Not useful at the moment.
    """

    def __init__(self, param):
        # set eventuali parametri
        self.param = param


class rand_movement(movement):
    """
    Define a random movement policy.
    """

    def __init__(self, param=None):
        movement.__init__(self, param)

    def move(self):
        """
        :return: a random direction where to move
        """
        possibility = ["N", "S", "W", "E"]
        direction = random.choice(possibility)
        return str(direction)


class rb_movement(movement):
    """
    Define a rule based movement policy
    """

    def __init__(self, param):
        movement.__init__(self, param)

    def move(self, actualMap, player, endx, endy):
        """
        :param actualMap: the map recieved from the server.
        :param player: the player structure to know his position.
        :param endx: the goal X coordinate.
        :param endy: the goal Y coordinate.
        :return: a specific direction where to move.
        """
        # for row in actualMap:
        #    print (row)

        path = findPath(actualMap, player, endx, endy)
        if len(path) < 2:
            return None, None
        else:
            coordinate = path[1]

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

            return direction, coordinate
