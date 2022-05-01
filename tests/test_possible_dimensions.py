
import sys
from pathlib import Path
from pytest import mark
import pudb

sys.path.append(str(Path(__file__).parents[1]))

from maze import *



params = mark.parametrize("territories, entrance_direction, x, y, min_possible_len, result",
                          (
                           ((
                             (-10, 100, -9, -100),
                            ),
                            0,
                            -7, -2,
                            2,
                            {
                             (-8, None, -2, None),
                            },
                           ),

                           ((
                             (-10, 100, -9, -100),
                             (-10, -11, -4, -100),
                            ),
                            0,
                            -7, -2,
                            2,
                            {
                             (-3, None, -2, None),
                             (-8, None, -2, -10),
                            },
                           ),

                           ((
                             (-10, 100, -9, -100),
                             (-10, -11, -4, -100),
                             (-10, 100, -5, -3),
                            ),
                            0,
                            -7, -2,
                            2,
                            {
                             (-3, None, -2, None),
                             (-4, None, -2, -10),
                             (-8, -4, -2, -10),
                            },
                           ),

                           ((
                             (-10, 100, -9, -100),
                             (-10, -11, -4, -100),
                             (-10, 100, -5, -3),
                             (-10, 100, -7, -4),
                             (-10, -10, -7, -100),
                            ),
                            0,
                            -7, -2,
                            2,
                            {
                             (-3, None, -2, None),
                             (-4, None, -2, -10),
                             (-6, -4, -2, -10),
                             (-8, -5, -2, -9),
                            },
                           ),

                           ((
                             (-10, 100, -9, -100),
                             (-10, -11, -4, -100),
                             (-10, 100, -5, -3),
                             (-10, 100, -7, -8),
                            ),
                            0,
                            -7, -2,
                            2,
                            {
                             (-3, None, -2, None),
                             (-4, None, -2, -10),
                             (-6, -4, -2, -10),
                            },
                           ),
                          ),
                         )











@params
def test_possible_dimensions(territories, entrance_direction, x, y, min_possible_len, result):

    assert absolute_coords_space(territories, entrance_direction, x, y, min_possible_len) == result
    assert absolute_coords_space(territories + ((100,101,101,100),), entrance_direction, x, y, min_possible_len) == result
    print(f"\n{possible_dimensions(territories, entrance_direction, x, y, min_possible_len)=}")
    print(f"\n{possible_dimensions(territories + ((100,101,101,100),), entrance_direction, x, y, min_possible_len)=}")

