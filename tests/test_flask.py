import os
import random
import subprocess
import sys
import time
from pathlib import Path



import pytest
import requests


POPEN_CWD = Path(__file__).parents[1]


HOST = 'http://127.0.0.1:5000'

@pytest.fixture(scope='session', autouse=True)
def pytest_sessionstart():
    server = subprocess.Popen([sys.executable, '-m', 'flask', 'run'], cwd=POPEN_CWD)
    time.sleep(1)

    os.chdir('maze_generators/kruskal')
    mg = subprocess.Popen([sys.executable, '-m', 'flask', 'run'], cwd=POPEN_CWD)
    time.sleep(1)
    yield
    
    server.terminate()
    mg.terminate()

def test_2_requests_for_origin():
    '''Test that 2 requests for the same segment give the same value, and that the second one doesn't change the maze.'''
    segment1 = requests.get(f'{HOST}/generateSegment', params={'row': 0, 'col': 0}).json()
    segment2 = requests.get(f'{HOST}/generateSegment', params={'row': 0, 'col': 0}).json()
    
    assert segment1 == segment2, 'Segment at origin changed between requests.'
    requests.delete(f'{HOST}/resetMaze')

def test_reset_maze():
    '''Test that maze state can be reset'''
    segment1 = requests.get(f'{HOST}/generateSegment', params={'row': 0, 'col': 0}).json()
    requests.delete(f'{HOST}/resetMaze')
    segment2 = requests.get(f'{HOST}/generateSegment', params={'row': 0, 'col': 0}).json()
    
    assert segment1 != segment2, 'Segment at origin is the same after reset and regeneration.'
    requests.delete(f'{HOST}/resetMaze')

def test_many_segments():
    states = {}

    # generate lots of segments
    for _ in range(30):
        coords = (random.randint(-100, 100), random.randint(-100, 100))
        segment = requests.get(f'{HOST}/generateSegment', params={'row': coords[0], 'col': coords[1]}).json()
        states[coords] = segment
    
    for coords, val in states.items():
        r = requests.get(f'{HOST}/generateSegment', params={'row': coords[0], 'col': coords[1]})
        assert r.json() == val, 'Segment changed between requests.'
