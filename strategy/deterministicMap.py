from data_structure.gameStatus import *


def deterministicMap(self):
    """
     CELLULAR AUTOMATA MAP. Discourage Karen to allign with enemies. If there is no other way, go and shoot.
     :param self: Karen
     :return: a weighted map
     """

    value = [int(self.maxWeight / 2), int(self.maxWeight / 4)]
    walkable = ["."]
    river = ["~"]
    trap = ["!"]
    obstacles = ["#", "@"]
    recharge = ["$"]
    barrier = ["&"]
    allies = game.allies.keys()
    enemies = game.enemies.keys()
    serverMap = game.serverMap
    weightedMap = [row[:] for row in serverMap]

    def recursiveMap(count, j, rec_weightedMap, weight):
        '''
        Recursive map generation. Resamble Cellular Automata decision adding weight to the map consistently with the distance from enemies
        :param count: the horizontal coordinate
        :param j: the vertical coordinate
        :param rec_weightedMap: the map
        :param weight: the weight of being in [i:,:j] position
        :return: a weighted map
        '''
        # da  muro a nemico
        for position in range(enemy.x, -1, -1):
            if rec_weightedMap[count][position] != '#' and rec_weightedMap[count][position] != "&":
                if isinstance(rec_weightedMap[count][position], int) is False:
                    rec_weightedMap[count][position] = weight
            else:
                break

        # da nemico a muro
        for position in range(enemy.x, len(rec_weightedMap[count])):
            if rec_weightedMap[count][position] != '#' and rec_weightedMap[count][position] != "&":
                if isinstance(rec_weightedMap[count][position], int) is False:
                    rec_weightedMap[count][position] = weight
            else:
                break

        # Controllo per colonne
        for position in range(enemy.y, -1, -1):
            if rec_weightedMap[position][j] != '#' and rec_weightedMap[position][j] != "&":
                if isinstance(rec_weightedMap[position][j], int) is False:
                    rec_weightedMap[position][j] = weight
            else:
                break

        for position in range(enemy.y, len(rec_weightedMap[j])):
            if rec_weightedMap[position][j] != '#' and rec_weightedMap[position][j] != "&":
                if isinstance(rec_weightedMap[position][j], int) is False:
                    rec_weightedMap[position][j] = weight
            else:
                break

        return rec_weightedMap

    # ---------------------------------------------------------------------------------------------------
    # For each enemy that is still alive, create a weighted map assigning value to all the position in the map around the enemy
    for enemykey in game.enemies.keys():
        enemy = game.enemies.get(enemykey)
        if enemy.state == "ACTIVE":
            # First call to assign weight to the enemy's 'x column' and 'y row' coordinate
            weightedMap = recursiveMap(enemy.y, enemy.x, weightedMap, int(self.maxWeight / 2))

            # Recursive calls giving the already weighted to assign weight to all the coordinate around the enemy player
            if enemy.y - 1 >= 0:
                if enemy.x - 1 >= 0:
                    weightedMap = recursiveMap(enemy.y - 1, enemy.x - 1, weightedMap, int(self.maxWeight / 4))
                if enemy.x + 1 < len(weightedMap[0]):
                    weightedMap = recursiveMap(enemy.y - 1, enemy.x + 1, weightedMap, int(self.maxWeight / 4))

            if enemy.y + 1 < len(weightedMap[0]):
                if enemy.x - 1 >= 0:
                    weightedMap = recursiveMap(enemy.y + 1, enemy.x - 1, weightedMap, int(self.maxWeight / 4))
                if enemy.x + 1 < len(weightedMap[0]):
                    weightedMap = recursiveMap(enemy.y + 1, enemy.x + 1, weightedMap, int(self.maxWeight / 4))

    # For each position, assign different weight considering their nature
    for i in range(0, game.mapHeight):
        for j in range(0, game.mapWidth):

            if weightedMap[i][j] in value:
                None

            elif serverMap[i][j] in walkable:
                weightedMap[i][j] = 1

            elif serverMap[i][j] in river:
                weightedMap[i][j] = int(self.maxWeight / 3)

            elif serverMap[i][j] in trap:
                weightedMap[i][j] = int(self.maxWeight)

            elif serverMap[i][j] in obstacles:
                weightedMap[i][j] = 0

            elif serverMap[i][j] in recharge:
                weightedMap[i][j] = 1

            elif serverMap[i][j] in barrier:
                weightedMap[i][j] = 0

            elif serverMap[i][j] == game.wantedFlagName:
                weightedMap[i][j] = 1

            elif serverMap[i][j] == game.toBeDefendedFlagName:
                weightedMap[i][j] = 0

            elif serverMap[i][j] in allies or serverMap[i][j] in enemies or serverMap[i][j] == self.me.symbol:
                weightedMap[i][j] = 1

    return weightedMap
