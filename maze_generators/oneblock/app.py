import random
from flask import Flask, jsonify 
import os
import sys
import inspect

import requests

current_dir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
parent_dir = os.path.dirname(parent_dir)
sys.path.insert(0, parent_dir)

from maze import *

app = Flask(__name__)

@app.route('/addMG', methods=['GET'])
def GET_addMG():
    response = requests.put('http://localhost:5000/addMG', json={
        "author": "aarya",
        "url": "http://localhost:24004",
        "name": "floating-block",
    })

    return jsonify(response.json()), response.status_code

@app.route('/generate', methods=['GET'])
def GET_generate():
    maze = Maze(7, 7)

    x = 3
    y = 3

    while x == 3:
        x = random.randint(1,5)

    while y == 3:
        y = random.randint(1,5)

    for dir in range(4):
        maze.add_wall(Coord(x, y), dir)

    print(maze.encode())

    maze = maze.add_boundary()
    return jsonify({'geom': maze.encode()}), 200