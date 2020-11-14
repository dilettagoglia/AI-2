import string

from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.finder.breadth_first import BreadthFirstFinder
# from pathfinding.finder.best_first import BestFirstFinder
from pathfinding.finder.dijkstra import DijkstraFinder
from pathfinding.finder.bi_a_star import BiAStarFinder  # the best one
from pathfinding.finder.ida_star import IDAStarFinder


# Any value smaller or equal to 0 describes an obstacle. Any number bigger than 0 describes the weight of a field
# that can be walked on. The bigger the number the higher the cost to walk that field.
# Only Dijkstra and A* take the weight of the fields on the map into account.

# You can use negative values to describe different types of obstacles.
# It does not make a difference for the path finding algorithm but it might be useful for your later map evaluation.


# Parsing function
def pathFinderParsing(actualMap):
    walkable = [".", "~"]
    trap = ["!"]
    obstacles = ["#", "@"]
    recharge = ["$"]
    barrier = ["&"]
    flags = ["x", "X"]
    players = list(string.ascii_letters)
    pathFinderMap = []
    # pathFinderMap = [[] for _ in range(32, 32)]
    # print(pathFinderMap)
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

            if actualMap[i][j] in flags:
                pathFinderMap[i].append(1)

            if actualMap[i][j] in players:
                pathFinderMap[i].append(1)

    return pathFinderMap


def findPath(actualMap, startx, starty, endx, endy):
    parsedMap = pathFinderParsing(actualMap)

    # dentro chiama il parsing
    for row in actualMap:
      print (row)
    print( " ")
    for row in parsedMap:
        print(row)

    grid = Grid(matrix=parsedMap)

    start = grid.node(startx, starty)
    end = grid.node(endx, endy)

    finder = BiAStarFinder(diagonal_movement=DiagonalMovement.never)
    path, runs = finder.find_path(start, end, grid)
    # The find_path function does not only return you the path from the start to the end point it also returns the number
    # of times the algorithm needed to be called until a way was found.

    print('operations:', runs, 'path length:', len(path))
    print(grid.grid_str(path=path, start=start, end=end))

    return path[1]





# Currently there are 6 path-finders bundled in this library:

#                                     OPERATIONS for path length = 24

# A*                                  108
# Dijkstra                            196
# Best-First                          ?
# Bi-directional A*                   67
# Breadth First Search (BFS)          196
# Iterative Deeping A* (IDA*)         661
