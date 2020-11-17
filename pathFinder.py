from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.bi_a_star import BiAStarFinder  # the best one
from pathfinding.finder.a_star import AStarFinder
from pathfinding.finder.breadth_first import BreadthFirstFinder
# from pathfinding.finder.best_first import BestFirstFinder
from pathfinding.finder.dijkstra import DijkstraFinder
from pathfinding.finder.ida_star import IDAStarFinder


# Any value smaller or equal to 0 describes an obstacle. Any number bigger than 0 describes the weight of a field
# that can be walked on. The bigger the number the higher the cost to walk that field.
# Only Dijkstra and A* take the weight of the fields on the map into account.

# You can use negative values to describe different types of obstacles.
# It does not make a difference for the path finding algorithm but it might be useful for your later map evaluation.


def pathFinderParsing(actualMap, game):
    """
    Parse the map received from the server.
    :param actualMap: the map received from the server.
    :param game: Game structure to access player position.
    :return: a numeric map used for PathFinder Algorithm.
    """
    walkable = [".", "~"]
    trap = ["!"]
    obstacles = ["#", "@"]
    recharge = ["$"]
    barrier = ["&"]
    allies = game.allies.keys()
    enemies = game.enemies.keys()


    pathFinderMap = []

    # For each cell in the map check if it is walkable, if it's a trap, obstacle or other stuff
    for i in range(0, len(actualMap[0])):
        pathFinderMap.append([])

        for j in range(0, len(actualMap[0])):

            if actualMap[i][j] in walkable:
                pathFinderMap[i].append(1)

            if actualMap[i][j] in trap:
                pathFinderMap[i].append(2)

            if actualMap[i][j] in obstacles:
                pathFinderMap[i].append(0)

            if actualMap[i][j] in recharge:
                pathFinderMap[i].append(1)

            if actualMap[i][j] in barrier:
                pathFinderMap[i].append(0)

            if actualMap[i][j] == game.wantedFlagName:
                pathFinderMap[i].append(1)

            if actualMap[i][j] == game.toBeDefendedFlagName:
                pathFinderMap[i].append(0)

            if actualMap[i][j] in allies or actualMap[i][j] in enemies or actualMap[i][j] == game.me.symbol:
                pathFinderMap[i].append(1)

    return pathFinderMap


def findPath(actualMap, player, game, endx, endy):
    """
    Apply an algorithm for path finding
    :param actualMap: the actual map from the server.
    :param player: Karen.
    :param game: the game structure with all the information.
    :param endx: the goal x coordinate.
    :param endy: the goal y cooridnate.
    :return: next position coordinates
    """
    parsedMap = pathFinderParsing(actualMap, game)

    grid = Grid(matrix=parsedMap)

    start = grid.node(player.x, player.y)
    end = grid.node(endx, endy)

    finder = BiAStarFinder(diagonal_movement=DiagonalMovement.never)
    path, runs = finder.find_path(start, end, grid)
    # The find_path function does not only return you the path from the start to the end point it also returns the number
    # of times the algorithm needed to be called until a way was found.

    print('operations:', runs, 'path length:', len(path))
    #print(grid.grid_str(path=path, start=start, end=end))

    return path[1]



# Currently there are 6 path-finders bundled in this library:

#                                     OPERATIONS for path length = 24

# A*                                  108
# Dijkstra                            196
# Best-First                          ?
# Bi-directional A*                   67
# Breadth First Search (BFS)          196
# Iterative Deeping A* (IDA*)         661
