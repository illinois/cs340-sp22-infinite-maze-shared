
import sys
from pathlib import Path
from pytest import parametrize

sys.path.append(str(Path(__file__).parents[1] / "infinite-maze"))

from possible_dimensions import possible_dimensions

@pytest.parametrize("territories, entrance_direction, x, y, min_possible_len, result",
                    (
                     (),
                     (),
                     (),
                     (),
                    ),
                   )
def test_possible_dimensions(territories, entrance_direction, x, y, min_possible_len, result):
