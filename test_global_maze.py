import random
from global_maze import GlobalMaze

def test_simple_set_get():
    maze_state = GlobalMaze()
    data = {'foo': 'bar', 'cs': 240}

    maze_state.set_state(0, 0, data)
    assert maze_state.get_state(0, 0) == data, 'Retrieved segment does not match.'

def test_reset():
    maze_state = GlobalMaze()
    data = {'foo': 'bar', 'cs': 240}

    maze_state.set_state(0, 0, data)
    maze_state.reset()
    assert maze_state.get_state(0, 0) == None, 'Segment at origin exists despite reset.'
    assert maze_state.get_full_state() == {}, 'Maze state not empty despite reset.'

def test_many_segments():
    maze_state = GlobalMaze()

    expected_states = {}
    for _ in range(100):
        expected_states[(random.randint(-100, 100), random.randint(-100, 100))] = {random.random(): random.random()}
    
    for key, val in expected_states.items():
        maze_state.set_state(key[0], key[1], val)
    
    for key, val in expected_states.items():
        assert maze_state.get_state(key[0], key[1]) == val, 'Retrieved state did not match expected.'
