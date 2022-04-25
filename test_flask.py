import os
import subprocess
import sys
import time

import pytest
import requests

HOST = 'http://127.0.0.1:5000'

@pytest.fixture(scope='session', autouse=True)
def pytest_sessionstart():
    server = subprocess.Popen([sys.executable, '-m', 'flask', 'run'])
    time.sleep(1)

    os.chdir('maze_generators/kruskal')
    mg = subprocess.Popen([sys.executable, '-m', 'flask', 'run'])
    time.sleep(1)
    yield
    
    server.terminate()
    mg.terminate()

def test_2_requests_for_origin():
    '''Test that 2 requests for the same segment give the same value, and that the second one doesn't change the maze.'''
    segment1 = requests.get(f'{HOST}/generateSegment', params={'row': 0, 'col': 0}).json()
    state1 = requests.get(f'{HOST}/mazeState').json()
    
    segment2 = requests.get(f'{HOST}/generateSegment', params={'row': 0, 'col': 0}).json()
    state2 = requests.get(f'{HOST}/mazeState').json()
    
    assert segment1 == segment2, 'Segment at origin changed between requests.'
    assert state1 == state2, 'Maze state changed between requests.'
    requests.delete(f'{HOST}/resetMaze')

def test_reset_maze():
    '''Test that `maze_state` can be reset'''
    segment1 = requests.get(f'{HOST}/generateSegment', params={'row': 0, 'col': 0}).json()
    state1 = requests.get(f'{HOST}/mazeState').json()

    requests.delete(f'{HOST}/resetMaze')
    assert requests.get(f'{HOST}/mazeState').json() == {}, 'Maze state has not been reset.'
    
    segment2 = requests.get(f'{HOST}/generateSegment', params={'row': 0, 'col': 0}).json()
    state2 = requests.get(f'{HOST}/mazeState').json()
    
    assert segment1 != segment2, 'Segment at origin is the same after reset and regeneration.'
    assert state1 != state2, 'Maze state is the same after reset and regeneration'
    requests.delete(f'{HOST}/resetMaze')
