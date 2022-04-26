#!/usr/bin/env python



from collections import namedtuple
import operator
from sortedcollections import SortedDict



def possible_dimensions(territories, entrance_direction, x, y, min_possible_len = 2):
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

    :param min_possible_len: a value indicating a hard minimum possible length.
    `2` by default, nobody wants a segment just 1 unit wide or it can't be a maze.
    Please don't make it less than that

    :type min_possible_len: int, optional

    :return: Returns multiple tuples of 4 ints.
    Each tuple is a possibility, there may be instances of >1 tuples based on
    the nature of obstructive territories.
        1st `int` is the maximum north protrusion.
        2nd `int` is the maximum east protrusion.
        3rd `int` is the maximum south protrusion.
        4th `int` is the maximum west protrusion.
    :rtype: set[tuple[int, int]]

    """


    # TODO: strictly validate parameters



    ed   = entrance_direction
    dc   = (entrance_direction + 1) % 4
    op   = entrance_direction ^ 0b10
    dcc  = (entrance_direction + 3) % 4

    # in X_key, X refers to direction from the iterating territory and returns True for smaller resulting boundaries (territory boundary, current position)

    op_key  = (lambda x: x) if op  & 0b10 else operator.neg
    # dc_key  = operator.neg  if dc  & 0b10 else (lambda x: x)
    # dcc_key = operator.neg  if dcc & 0b10 else (lambda x: x)

    # in X_cmp, X refers to direction from the iterating territory and returns True for smaller resulting boundaries (territory boundary, current position)

    ed_cmp  = operator.gt if ed  & 0b10 else operator.lt # < if north
    dc_cmp  = operator.lt if dc  & 0b10 else operator.gt # > if north
    op_cmp  = operator.gt if op  & 0b10 else operator.lt # > if north
    dcc_cmp = operator.lt if dcc & 0b10 else operator.gt # < if north

    c  = (x, y)
    pe = ed & 0b1 # 1 if north
    pa = pe ^ 0b1 # 0 if north

    hards = [None] * 4
    hards[op] = c[pa] # if north, south boundary will be y-coord


    for territory in territories:
        b = territory["bounds"]

        if op_cmp(b[op], c[pa] - op_key(min_possible_len)): # if north, and south boundary of territory > y - min_possible_len
            if dcc_cmp(b[dc], c[pe]): # if north, and east boundary of territory < x
                if hards[dcc] is None or dc_cmp(b[dc], hards[dcc]): # max
                    hards[dcc] = b[dc]

            elif dc_cmp(b[dcc], c[pe]): # if north, and west boundary of territory > x
                if hards[dc] is None or dcc_cmp(b[dcc], hards[dc]): # min
                    hards[dc] = b[dcc]


        elif not dcc_cmp(b[dc], c[pe]) and not dc_cmp(b[dcc], c[pe]): # if north, and east >= x and west <= x
            if hards[ed] is None or op_cmp(b[op], hards[ed]): # max
                hards[ed] = b[op]


    # in X_data, X refers to a direction of own boundary
    dc_data  = SortedDict(key=op_key)
    dcc_data = SortedDict(key=op_key)

    for territory in territories:
        b = territory["bounds"]

        if op_cmp(b[op], hards[ed]):
            if dc_cmp(b[dc], hards[dcc]): # if north, from west side

                if b[op] not in dcc_data or dc_cmp(b[dc], dcc_data[b[op]]):
                    dcc_data[b[op]] = b[dc] # if north, want west of own boundary set conservatively increasing

            elif dcc_cmp(b[dcc], hards[dc]): # if north, from east side

                if b[op] not in dc_data or dcc_cmp(b[dcc], dc_data[b[op]]):
                    dc_data[b[op]] = b[dcc] # if north, want east of own boundary set conservatively decreasing


    dc_items  = list(dc_data.items() )
    dcc_items = list(dcc_data.items())

    # TODO: iterate both dc_items and dcc_items based on key values to return possibilities
