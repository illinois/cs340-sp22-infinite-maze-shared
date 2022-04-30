import random

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parents[1]))

from global_maze import GlobalMaze

class TestBasics:
    def test_simple_set_get(self):
        maze_state = GlobalMaze()
        data = {'foo': 'bar', 'cs': 240}

        maze_state.set_state(0, 0, data)
        assert maze_state.get_state(0, 0) == data, 'Retrieved segment does not match.'

    def test_reset(self):
        maze_state = GlobalMaze()
        data = {'foo': 'bar', 'cs': 240}

        maze_state.set_state(0, 0, data)
        maze_state.reset()
        assert maze_state.get_state(0, 0) == None, 'Segment at origin exists despite reset.'
        assert maze_state.is_empty(), 'Maze state not empty despite reset.'

    def test_many_segments(self):
        maze_state = GlobalMaze()

        expected_states = {}
        for _ in range(100):
            expected_states[(random.randint(-100, 100), random.randint(-100, 100))] = {random.random(): random.random()}
        
        for key, val in expected_states.items():
            maze_state.set_state(key[0], key[1], val)
        
        for key, val in expected_states.items():
            assert maze_state.get_state(key[0], key[1]) == val, 'Retrieved state did not match expected.'

class TestFreeSpace:
    def test_basic_scan(self):
        maze_state = GlobalMaze()
        data = {'cs': 240}

        maze_state.set_state(-1, -1, data)
        maze_state.set_state(-1, 0, data)
        maze_state.set_state(-1, 1, data)

        maze_state.set_state(0, -1, data)
        maze_state.set_state(0, 0, data)
        # leave (0, 1) empty

        maze_state.set_state(1, -1, data)
        maze_state.set_state(1, 0, data)
        maze_state.set_state(1, 1, data)

        assert maze_state.get_free_space(0, 0, 1) == {(0, 1)}, 'Free space did not match expected.'

    def test_scan_far(self):
        maze_state = GlobalMaze()
        data = {'cs': 240}

        for row in range(20, 23):
            for col in range(20, 23):
                if (row, col) != (21, 22):
                    maze_state.set_state(row, col, data)
        
        assert maze_state.get_free_space(21, 21, 1) == {(21, 22)}
