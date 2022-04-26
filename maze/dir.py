from maze.coord import Coord

"""The direction constants aare defined as follows because these values are used to encode the cell in the maze.
In particular for any direction i, the cell value has a bit set at position 1<<i iff it has a wall in the direction i."""
WEST = 0
SOUTH = 1
EAST = 2
NORTH = 3


"""
The direction vector array tells us the vector, which when added to a coord gives the next coord, after moving in that particular direction.
The indices of the directions match the directions specified by the constants NORTH, SOUTH, EAST, WEST.
"""
dir_vec_arr = [None]*4
dir_vec_arr[NORTH] = (0, -1)
dir_vec_arr[SOUTH] = (0, 1)
dir_vec_arr[EAST] = (1, 0)
dir_vec_arr[WEST] = (-1, 0)


def sgn(x: int):
    """Determines the sign of a number."""
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0


def get_direction(first: Coord, second: Coord) -> int:
    """Gets the unit direction that moves the first coord in the direction of the second coord, if they are one of NORTH, SOUTH, EAST or WEST only."""
    dx = sgn(second.col - first.col)
    dy = sgn(second.row - first.row)

    for i, d in enumerate(dir_vec_arr):
        dx1, dy1 = d
        if dx == dx1 and dy == dy1:
            return i

    return -1
