
import sys
from pathlib import Path
from pytest import mark
import pudb

sys.path.append(str(Path(__file__).parents[1] / "infinite-maze"))

from possible_dimensions import possible_dimensions

@mark.parametrize("territories, entrance_direction, x, y, min_possible_len, result",
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
                    ),
                   )
def test_possible_dimensions(territories, entrance_direction, x, y, min_possible_len, result):
    # if len(territories) == 2:
    #     pudb.set_trace()
    assert possible_dimensions(territories, entrance_direction, x, y, min_possible_len) == result
