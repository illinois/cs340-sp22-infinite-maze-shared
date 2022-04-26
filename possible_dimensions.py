#!/usr/bin/env python



def possible_dimensions(territories, entrance_direction, x, y):
    """Returns a list of possible dimensions that can be used to ensure that
    a newly generated segment will not collide with already-existing segments as a pure function.

    Input coordinates must not be in a territory, must be as in unexplored space
    just before a segment generates.

    *Do not call this when generating the very first segment as it will not make sense.*

    :param territories: an iterable of tuples of 4 ints.
        Each tuple represents an occupied maze segment and their rectangle boundaries.
        1st `int` is the y-coordinate of the north side.
        2nd `int` is the x-coordinate of the east side.
        3rd `int` is the y-coordinate of the south side.
        4th `int` is the x-coordinate of the west side.
        All coordinates whose x-value is in `[territory[3], territory[1]]`
        and y-value is in `[territory[0], territory[2]]` is considered part of the territory
        and must be respected by the function.
    :type territories: Iterable[tuple[int, int, int, int]]

    :param entrance_direction: Indicates direction the new segment will be generated towards.
        0 <- north
        1 <- east
        2 <- south
        3 <- west
    Any other different values are not allowed.
    :type entrance_direction: int

    :param x: X-coordinate of player, higher values go towards east.
    :type x: int

    :param y: Y-coordinate of player, higher values go towards south.
    :type y: int

    :return: Returns multiple tuples of 4 ints.
    Each tuple is a possibility, there may be instances of >1 tuples based on
    the nature of obstructive territories.
        1st `int` is the maximum north protrusion.
        2nd `int` is the maximum east protrusion.
        3rd `int` is the maximum south protrusion.
        4th `int` is the maximum west protrusion.
    :rtype: set[tuple[int, int]]

    """
    pass

