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