from random import randint
from flask import Flask, jsonify
from .custom_mg import CustomMazeGenerator

app = Flask(__name__)

Letter_0 = [
    'xxx.xxx',
    '.......',
    '..xxx.x',
    '..x.x..',
    '..xxx..',
    '.......',
    'xxx.xxx',
]

Letter_1 = [
    'xx...xx',
    '.......',
    '..x.x..',
    '.......',
    '..x.x..',
    '.......',
    'xx...xx',
]

Stair_0 = [
    ".xxxx.",
    "..xxx.",
    "...xx.",
    "....x.",
]

Stair_1 = [
    ".xxxx.",
    ".xxx..",
    ".xx...",
    ".x....",
],

letter_maps = [
    Stair_0,
    Stair_1,
    Letter_0,
    Letter_1
]


@app.route('/generate', methods=["GET"])
def GET_maze_segment():
    selected_map = randint(0, len(letter_maps)-1)
    print("Selected map: " + str(selected_map))
    letter_map = letter_maps[selected_map]
    maze = CustomMazeGenerator(7, 7, letter_map).create()
    maze = maze.expand_maze_with_blank_space(7,7)
    maze = maze.add_boundary()
    response = jsonify({"geom": maze.encode()})
    response.headers["Cache-Control"] = 'no-store'
    return response, 200
