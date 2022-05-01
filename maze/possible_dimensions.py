#!/usr/bin/env python



from collections import deque, namedtuple
from collections.abc import Iterable, Sequence
from copy import copy
import operator
from sortedcontainers import SortedDict, SortedKeyList



def __type_assert(b, message):
    if not b:
        raise TypeError(message)

def __value_assert(b, message):
    if not b:
        raise ValueError(message)


_identity = lambda x: x

_RelativeCoordsTuple = namedtuple("_RelativeCoords",
                                  (
                                   "ed",
                                   "dc",
                                   "op",
                                   "dcc",
                                   "ed_key",
                                   "dc_key",
                                   "op_key",
                                   "dcc_key",
                                   "ed_cmp",
                                   "dc_cmp",
                                   "op_cmp",
                                   "dcc_cmp",
                                   "c",
                                   "pe",
                                   "pa",
                                  ),
                                 )

_PossibilityTuple = namedtuple("_PossibilityTuple",
                               (
                                "width",
                                "height",
                                "x_offset",
                                "y_offset",
                               ),
                              )


class _RelativeCoords(_RelativeCoordsTuple):

    def __new__(cls, entrance_direction, x, y):

        ed   = entrance_direction
        dc   = (entrance_direction + 1) % 4
        op   = entrance_direction ^ 0b10
        dcc  = (entrance_direction + 3) % 4

        # in X_key, X refers to direction from the iterating territory and returns True for smaller resulting boundaries (territory boundary, current position)

        ed_key  = _identity     if ed  & 0b10 else operator.neg
        dc_key  = operator.neg  if dc  & 0b10 else _identity
        op_key  = _identity     if op  & 0b10 else operator.neg
        dcc_key = operator.neg  if dcc & 0b10 else _identity

        # in X_cmp, X refers to direction from the iterating territory and returns True for smaller resulting boundaries (territory boundary, current position)

        ed_cmp  = operator.gt if ed  & 0b10 else operator.lt # < if north
        dc_cmp  = operator.lt if dc  & 0b10 else operator.gt # > if north
        op_cmp  = operator.gt if op  & 0b10 else operator.lt # > if north
        dcc_cmp = operator.lt if dcc & 0b10 else operator.gt # < if north

        c  = (x, y)
        pe = ed & 0b1 # 0 if north
        pa = pe ^ 0b1 # 1 if north

        return super().__new__(cls,
                               ed=ed,
                               dc=dc,
                               op=op,
                               dcc=dcc,
                               ed_key=ed_key,
                               dc_key=dc_key,
                               op_key=op_key,
                               dcc_key=dcc_key,
                               ed_cmp=ed_cmp,
                               dc_cmp=dc_cmp,
                               op_cmp=op_cmp,
                               dcc_cmp=dcc_cmp,
                               c=c,
                               pe=pe,
                               pa=pa,
                              )







class PossibilityInfo(_PossibilityTuple):

    def __new__(cls, entrance_direction, x, y, possibility):

        rc = _RelativeCoords(entrance_direction, x, y)

        dimensions = [None] * 2
        offset_coords = [0] * 2

        pe_limits = (possibility[rc.dc] is None, possibility[rc.dcc] is None)

        if pe_limits == (False, True):
            offset_coords[rc.pe] = abs(possibility[rc.dc] - rc.c[rc.pe])
            if rc.dc & 0b10:
                offset_coords[rc.pe] *= -1

        elif pe_limits == (True, False):
            offset_coords[rc.pe] = abs(possibility[rc.dcc] - rc.c[rc.pe])
            if rc.dcc & 0b10:
                offset_coords[rc.pe] *= -1

        elif pe_limits == (False, False):
            dimensions[rc.pe] = abs(possibility[rc.dc] - possibility[rc.dcc]) + 1,
            offset_coords[rc.pe] = rc.c[rc.pe] - min(possibility[rc.dc], possibility[rc.dcc])



        if possibility[rc.ed] is not None:
            dimensions[rc.pa] = abs(possibility[rc.ed] - rc.c[rc.pa]) + 1

        return super().__new__(
                               cls,
                               *dimensions,
                               *offset_coords,
                              )






def absolute_coords_space(territories, entrance_direction, x, y, min_possible_len = 2):
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
        1st `int` is the north bound.
        2nd `int` is the east bound.
        3rd `int` is the south bound.
        4th `int` is the west bound.
    Values inside tuple can also be None, meaning no limiting bound.
    :rtype: set[tuple[int, int, int, int]]

    """


    __type_assert(isinstance(territories, Iterable), "'territories' must be iterable")
    __type_assert(type(entrance_direction) == int, "'entrance_direction' must be int")
    __value_assert(entrance_direction in range(4), "'entrance_direction' must be [0, 4)")
    __type_assert(type(x) == int, "'x' must be int")
    __type_assert(type(y) == int, "'y' must be int")
    __type_assert(type(min_possible_len) == int, "'min_possible_len' must be int")
    __value_assert(min_possible_len >= 2, "'min_possible_len' must be >= 2")


    territories = tuple(territories)

    rc = _RelativeCoords(entrance_direction, x, y)

    hards = [None] * 4
    hards[rc.op] = rc.c[rc.pa] # if north, south boundary will be y-coord


    for territory in territories:

        __type_assert(isinstance(territory, Sequence), "all territories must be a sequence")
        __value_assert(
                           len(territory) == 4
                       and all(type(direction) == int for direction in territory),
                       "all territories must be 4-int tuples",
                      )

        if (
                rc.op_cmp(territory[rc.op], hards[rc.op] - rc.op_key(min_possible_len))
            and rc.ed_cmp(territory[rc.ed], hards[rc.op])
           ): # if north, and south boundary of territory > y - min_possible_len

            dcc_b = territory[rc.dc ] + rc.dc_key(1)
            dc_b  = territory[rc.dcc] + rc.dcc_key(1)

            if rc.dcc_cmp(territory[rc.dc], rc.c[rc.pe]): # if north, and east boundary of territory < x
                if hards[rc.dcc] is None or rc.dc_cmp(territory[rc.dc], hards[rc.dcc]): # max
                    hards[rc.dcc] = territory[rc.dc]

            elif rc.dc_cmp(territory[rc.dcc], rc.c[rc.pe]): # if north, and west boundary of territory > x
                if hards[rc.dc] is None or rc.dcc_cmp(territory[rc.dcc], hards[rc.dc]): # min
                    hards[rc.dc] = territory[rc.dcc]


        elif (
                  not rc.dcc_cmp(territory[rc.dc], rc.c[rc.pe])
              and not rc.dc_cmp(territory[rc.dcc], rc.c[rc.pe])
             ): # if north, and east >= x and west <= x

            ed_b = territory[rc.op] + rc.op_key(1)
            if hards[rc.ed] is None or rc.op_cmp(ed_b, hards[rc.ed]): # max
                hards[rc.ed] = ed_b


    # in X_data, X refers to a direction of own boundary
    dc_data  = SortedDict(rc.ed_key)
    dcc_data = SortedDict(rc.ed_key)

    for territory in territories:

        ed_b = territory[rc.op] + rc.op_key(1)

        if (        rc.op_cmp(ed_b, hards[rc.ed])
            and not rc.op_cmp(territory[rc.op], hards[rc.op] - rc.op_key(min_possible_len))
           ):

            dcc_b = territory[rc.dc ] + rc.dc_key(1)
            dc_b  = territory[rc.dcc] + rc.dcc_key(1)

            if (    rc.dcc_cmp(dcc_b, rc.c[rc.pe])
                and (hards[rc.dcc] is None or rc.dc_cmp(dcc_b, hards[rc.dcc]))
               ): # if north, from west side

                if ed_b not in dcc_data:
                    skl = SortedKeyList(dcc_data.keys())
                    ind = skl.bisect_key_left(ed_b) - 1

                    if ind >= 0 and not rc.dc_cmp(dcc_b, dcc_data.peekitem(ind)[1]):
                        continue

                elif not rc.dc_cmp(dcc_b, dcc_data[ed_b]):
                    continue

                dcc_data[ed_b] = dcc_b # if north, want west of own boundary set conservatively increasing

            elif (    rc.dc_cmp(dc_b, rc.c[rc.pe])
                  and (hards[rc.dc] is None or rc.dcc_cmp(dc_b, hards[rc.dc]))
                 ): # if north, from east side

                if ed_b not in dc_data:
                    skl = SortedKeyList(dc_data.keys())
                    ind = skl.bisect_key_left(ed_b) - 1

                    if ind >= 0 and not rc.dcc_cmp(dc_b, dc_data.peekitem(ind)[1]):
                        continue

                elif not rc.dcc_cmp(dc_b, dc_data[ed_b]):
                    continue

                dc_data[ed_b] = dc_b # if north, want east of own boundary set conservatively decreasing





    dc_items  = deque(dc_data.items() )
    dcc_items = deque(dcc_data.items())

    possibilities_output = set()

    cur_possibility = copy(hards)


    def take_one(which_deque, direction):
        pair = which_deque.popleft()

        cur_possibility[rc.ed] = pair[0]

        possibilities_output.add(tuple(cur_possibility))

        cur_possibility[direction] = pair[1]




    def take_both():

        dc_pair = dc_items.popleft()
        dcc_pair = dcc_items.popleft()

        cur_possibility[rc.ed] = dc_pair[0]

        possibilities_output.add(tuple(cur_possibility))

        cur_possibility[rc.dc] = dc_pair[1]
        cur_possibility[rc.dcc] = dcc_pair[1]


    short_height = False

    while len(dc_items) > 0 or len(dcc_items) > 0:

        short_height = (
                            cur_possibility[rc.dc]  is not None
                        and cur_possibility[rc.dcc] is not None
                        and abs(cur_possibility[rc.dc] - cur_possibility[rc.dcc]) + 1 < min_possible_len
                       )

        if short_height:
            break


        if len(dc_items) > 0 and len(dcc_items) > 0:
            if dc_items[0][0] == dcc_items[0][0]:
                take_both()
            elif rc.op_cmp(dc_items[0][0], dcc_items[0][0]):
                take_one(dc_items, rc.dc)
            else:
                take_one(dcc_items, rc.dcc)

        elif len(dc_items) == 0:
            take_one(dcc_items, rc.dcc)

        else:
            take_one(dc_items, rc.dc)


    if not short_height:
        cur_possibility[rc.ed] = hards[rc.ed]

        possibilities_output.add(tuple(cur_possibility))

    return possibilities_output

    # TODO: iterate both dc_items and dcc_items based on key values to return possibilities

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
        1st `int` is the width.
        2nd `int` is the height.
        3rd `int` is x-axis offset (higher values mean shift whole segment towards west).
        4th `int` is y-axis offset (higher values mean shift whole segment towards north).
    1st int can be None meaning unlimited width.
    2nd int can be None meaning unlimited height.
    3rd int can be negative only if west side isn't bounded but east side is.
    4th int can be negative only if north side isn't bounded but south side is.
    :rtype: set[tuple[int, int, int, int]]

    """

    absolute_coords = absolute_coords_space(territories, entrance_direction, x, y, min_possible_len)

    return {PossibilityInfo(entrance_direction, x, y, possibility) for possibility in absolute_coords}

