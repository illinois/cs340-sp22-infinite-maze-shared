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
    r = requests.get(f'{HOST}/generateSegment', params={'row': 0, 'col': 0})
    segment1 = r.json()
    r = requests.get(f'{HOST}/mazeState')
    state1 = r.json()

    r = requests.get(f'{HOST}/generateSegment', params={'row': 0, 'col': 0})
    segment2 = r.json()
    r = requests.get(f'{HOST}/mazeState')
    state2 = r.json()

    assert segment1 == segment2, 'Segment at origin changed between requests.'
    assert state1 == state2, 'Maze state changed between requests.'

