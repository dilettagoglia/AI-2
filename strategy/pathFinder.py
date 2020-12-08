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


def findPath4Fuzzy(weightedMap, startx, starty, endx, endy):
    """
    Apply an algorithm for path finding
    :param weightedMap: the weighted and parsed map
    :param player: the AI player object.
    :param endx: the goal x coordinate.
    :param endy: the goal y cooridnate.
    :return: next position coordinates
    """

    grid = Grid(matrix=weightedMap)

    start = grid.node(startx, starty)
    end = grid.node(endx, endy)

    finder = AStarFinder(diagonal_movement=DiagonalMovement.never)
    path, runs = finder.find_path(start, end, grid)
    # The find_path function does not only return you the path from the start to the end point it also returns the number
    # of times the algorithm needed to be called until a way was found.

    # print('operations:', runs, 'path length:', len(path))
    # print(grid.grid_str(path=path, start=start, end=end))

    return path




def findPath(weightedMap, player, endx, endy):
    """
    Apply an algorithm for path finding
    :param weightedMap: the weighted and parsed map
    :param player: the AI player object.
    :param endx: the goal x coordinate.
    :param endy: the goal y cooridnate.
    :return: next position coordinates
    """


    grid = Grid(matrix=weightedMap)

    start = grid.node(player.x, player.y)
    end = grid.node(endx, endy)

    finder = AStarFinder(diagonal_movement=DiagonalMovement.never)
    path, runs = finder.find_path(start, end, grid)
    # The find_path function does not only return you the path from the start to the end point it also returns the number
    # of times the algorithm needed to be called until a way was found.

    # print('operations:', runs, 'path length:', len(path))
    # print(grid.grid_str(path=path, start=start, end=end))

    return path



# Currently there are 6 path-finders bundled in this library:

#                                     OPERATIONS for path length = 24

# A*                                  108
# Dijkstra                            196
# Best-First                          ?
# Bi-directional A*                   67
# Breadth First Search (BFS)          196
# Iterative Deeping A* (IDA*)         661
