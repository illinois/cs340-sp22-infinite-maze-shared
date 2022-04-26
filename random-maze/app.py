from random import randint
from flask import Flask, jsonify, request
from maze.maze import *
from maze.coord import *
from maze.dir import *
from random_mg import RandomMazeGenerator, expandIntoLargerMaze

app = Flask(__name__)

min_size = 3
max_size = 7


@app.route('/', methods=["GET"])
@app.route('/generate', methods=["GET"])
def GET_maze_segment():
    height = request.args.get('height') or randint(min_size, max_size)
    width = request.args.get('width') or randint(min_size, max_size)

    maze = RandomMazeGenerator(height, width).create()

    print(f"height:{height}, width:{width}")
    print(maze.encode())

    maze = expandIntoLargerMaze(maze, 7, 7)

    response = jsonify({"geom": maze.encode()})
    response.headers["Cache-Control"] = 'no-store'

    return response, 200
