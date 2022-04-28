#!/usr/bin/env python



from collections import deque
from copy import copy
import operator
from sortedcontainers import SortedDict, SortedKeyList




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

    identity = (lambda x: x)

    # in X_key, X refers to direction from the iterating territory and returns True for smaller resulting boundaries (territory boundary, current position)

    op_key  = identity      if op  & 0b10 else operator.neg
    dc_key  = operator.neg  if dc  & 0b10 else identity
    dcc_key = operator.neg  if dcc & 0b10 else identity

    # in X_cmp, X refers to direction from the iterating territory and returns True for smaller resulting boundaries (territory boundary, current position)

    gt = lambda a, b: b is None or a > b
    lt = lambda a, b: b is None or a < b

    ed_cmp  = gt if ed  & 0b10 else lt # < if north
    dc_cmp  = lt if dc  & 0b10 else gt # > if north
    op_cmp  = gt if op  & 0b10 else lt # > if north
    dcc_cmp = lt if dcc & 0b10 else gt # < if north

    c  = (x, y)
    pe = ed & 0b1 # 1 if north
    pa = pe ^ 0b1 # 0 if north

    hards = [None] * 4
    hards[op] = c[pa] # if north, south boundary will be y-coord


    for territory in territories:

        if op_cmp(territory[op], c[pa] - op_key(min_possible_len)): # if north, and south boundary of territory > y - min_possible_len

            dcc_b = territory[dc ] + dc_key(1)
            dc_b  = territory[dcc] + dcc_key(1)

            if dcc_cmp(territory[dc], c[pe]): # if north, and east boundary of territory < x
                if dc_cmp(territory[dc], hards[dcc]): # max
                    hards[dcc] = territory[dc]

            elif dc_cmp(territory[dcc], c[pe]): # if north, and west boundary of territory > x
                if dcc_cmp(territory[dcc], hards[dc]): # min
                    hards[dc] = territory[dcc]


        elif not dc_cmp(territory[dcc], c[pe]): # if north, and east >= x and west <= x
            ed_b = territory[op] + op_key(1)
            if op_cmp(ed_b, hards[ed]): # max
                hards[ed] = ed_b


    # in X_data, X refers to a direction of own boundary
    dc_data  = SortedDict(op_key)
    dcc_data = SortedDict(op_key)

    for territory in territories:

        ed_b = territory[op] + op_key(1)

        if op_cmp(ed_b, hards[ed]):

            dcc_b = territory[dc ] + dc_key(1)
            dc_b  = territory[dcc] + dcc_key(1)

            if dc_cmp(dcc_b, hards[dcc]): # if north, from west side

                if ed_b not in dcc_data:
                    skl = SortedKeyList(dcc_data.keys())
                    ind = skl.bisect_key_left(ed_b) - 1

                    if ind >= 0 and not dc_cmp(dcc_b, dcc_data.peekitem(ind)[1]):
                        continue

                elif not dc_cmp(dcc_b, dcc_data[ed_b]):
                    continue

                dcc_data[ed_b] = dcc_b # if north, want west of own boundary set conservatively increasing

            elif dcc_cmp(dc_b, hards[dc]): # if north, from east side

                if ed_b not in dc_data:
                    skl = SortedKeyList(dc_data.keys())
                    ind = skl.bisect_key_left(ed_b) - 1

                    if ind >= 0 and not dcc_cmp(dc_b, dc_data.peekitem(ind)[1]):
                        continue

                elif not dcc_cmp(dc_b, dc_data[ed_b]):
                    continue

                dc_data[ed_b] = dc_b # if north, want east of own boundary set conservatively decreasing





    dc_items  = deque(dc_data.items() )
    dcc_items = deque(dcc_data.items())

    possibilites_output = set()

    dc_bound = hards[dc]
    dcc_bound = hards[dcc]

    cur_possibility = copy(hards)

    while len(dc_items) > 0 or len(dcc_items) > 0:
        if len(dcc_items) == 0 or dc_items[0][0] < dcc_items[0][0]:

            pair = dc_items.popleft()

            cur_possibility[ed] = pair[0] - 1

            possibilites_output.add(tuple(cur_possibility))

            cur_possibility[dc] = pair[1]

        elif len(dc_items) == 0 or dc_items[0][0] > dcc_items[0][0]:

            pair = dcc_items.popleft()

            cur_possibility[ed] = pair[0]

            possibilites_output.add(tuple(cur_possibility))

            cur_possibility[ddc] = pair[1]

        else:
            dc_pair = dc_items.popleft()
            dcc_pair = dcc_items.popleft()

            cur_possibility[ed] = dc_pair[0]

            possibilites_output.add(tuple(cur_possibility))

            cur_possibility[dc] = dc_pair[1]
            cur_possibility[dcc] = dcc_pair[1]


    assert len(dc_items) == len(dcc_items)

    cur_possibility[ed] = hards[ed]

    possibilites_output.add(tuple(cur_possibility))

    return possibilites_output

    # TODO: iterate both dc_items and dcc_items based on key values to return possibilities
