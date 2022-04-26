from flask import Flask, jsonify
import os
import sys
import inspect

current_dir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from maze import *

app = Flask(__name__)


def get_maze():
    height = 7
    width = 7
    maze = Maze(height=height, width=width)

    pattern = []

    for y in range(7):
        row = ''
        for x in range(7):
            if abs(y-x) < 2:
                row += '.'
            else:
                row += 'x'
        print(row)
        pattern.append(row)

    for row in range(7):
        for col in range(7):
            if pattern[row][col] == 'x':
                continue

            for i in range(4):
                dx, dy = dir_vec_arr[i]

                x = col + dx
                y = row + dy

                if not maze.is_valid(Coord(y, x)):
                    continue

                if pattern[y][x] == 'x':
                    maze.add_wall(Coord(row, col), i)

    return maze


@app.route('/generate', methods=["GET"])
def GET_maze_segment():
    maze = get_maze()
    response = jsonify({"geom": maze.encode()})
    response.headers["Cache-Control"] = f"public,max-age={365*24*60*60}"
    response.headers["Age"] = 0
    return response, 200
