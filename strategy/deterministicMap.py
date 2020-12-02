def deterministicMap(self):
    """
     CELLULAR AUTOMATA MAP. Discourage Karen to allign with enemies. If there is no other way, go and shoot.
     :param self: Karen
     :param actualMap: the map retrieved from the server.
     :return: a weighted map
     """

    value = [int(self.mapSize / 2), int(self.mapSize / 4)]
    walkable = ["."]
    river = ["~"]
    trap = ["!"]
    obstacles = ["#", "@"]
    recharge = ["$"]
    barrier = ["&"]
    allies = self.game.allies.keys()
    enemies = self.game.enemies.keys()
    serverMap = self.game.serverMap
    weightedMap = [row[:] for row in serverMap]

    def recursiveMap(i, j, rec_weightedMap, weight):
        '''
        Recursive map generation. Resamble Cellular Automata decision adding weight to the map consistently with the distance from enemies
        :param i: the horizontal coordinate
        :param j: the vertical coordinate
        :param rec_weightedMap: the map
        :param weight: the weight of being in [i:,:j] position
        :return: a weighted map
        '''
        # da  muro a nemico
        for position in range(enemy.x, -1, -1):
            if rec_weightedMap[i][position] != '#' and rec_weightedMap[i][position] != "&":
                if isinstance(rec_weightedMap[i][position], int) is False:
                    rec_weightedMap[i][position] = weight
            else:
                break

        # da nemico a muro
        for position in range(enemy.x, len(rec_weightedMap[i])):
            if rec_weightedMap[i][position] != '#' and rec_weightedMap[i][position] != "&":
                if isinstance(rec_weightedMap[i][position], int) is False:
                    rec_weightedMap[i][position] = weight
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
    for enemykey in self.game.enemies.keys():
        enemy = self.game.enemies.get(enemykey)
        if enemy.state == "ACTIVE":
            # First call to assign weight to the enemy's 'x column' and 'y row' coordinate
            weightedMap = recursiveMap(enemy.y, enemy.x, weightedMap, int(self.mapSize / 2))

            # Recursive calls giving the already weighted to assign weight to all the coordinate around the enemy player
            if enemy.y - 1 >= 0:
                if enemy.x - 1 >= 0:
                    weightedMap = recursiveMap(enemy.y - 1, enemy.x - 1, weightedMap, int(self.mapSize / 4))
                if enemy.x + 1 < len(weightedMap[0]):
                    weightedMap = recursiveMap(enemy.y - 1, enemy.x + 1, weightedMap, int(self.mapSize / 4))

            if enemy.y + 1 < len(weightedMap[0]):
                if enemy.x - 1 >= 0:
                    weightedMap = recursiveMap(enemy.y + 1, enemy.x - 1, weightedMap, int(self.mapSize / 4))
                if enemy.x + 1 < len(weightedMap[0]):
                    weightedMap = recursiveMap(enemy.y + 1, enemy.x + 1, weightedMap, int(self.mapSize / 4))

    # For each position, assign different weight considering their nature
    for i in range(0, len(serverMap[0])):
        for j in range(0, len(serverMap[0])):

            if weightedMap[i][j] in value:
                None

            elif serverMap[i][j] in walkable:
                weightedMap[i][j] = 1

            elif serverMap[i][j] in river:
                weightedMap[i][j] = int(self.mapSize / 3)

            elif serverMap[i][j] in trap:
                weightedMap[i][j] = int(self.mapSize)

            elif serverMap[i][j] in obstacles:
                weightedMap[i][j] = 0

            elif serverMap[i][j] in recharge:
                weightedMap[i][j] = 1

            elif serverMap[i][j] in barrier:
                weightedMap[i][j] = 0

            elif serverMap[i][j] == self.game.wantedFlagName:
                weightedMap[i][j] = 1

            elif serverMap[i][j] == self.game.toBeDefendedFlagName:
                weightedMap[i][j] = 0

            elif serverMap[i][j] in allies or serverMap[i][j] in enemies or serverMap[i][j] == self.me.symbol:
                weightedMap[i][j] = 1

    return weightedMap