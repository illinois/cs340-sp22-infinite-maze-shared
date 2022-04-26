from random import randint
from flask import Flask, jsonify, request
from custom_mg import CustomMazeGenerator

app = Flask(__name__)

letter_maps = [
    [
        'x.x.x',
        'x.x.x',
        'x.x.x',
        'x...x',
        'xx.xx',
    ],

    [
        "xxx",
        ".x.",
        "xxx",
        ".x.",
        "xxx"
    ],

    [
        "xxxx",
        ".xxx",
        "..xx",
        "...x",
    ],

    [
        "xxxx",
        "xxx.",
        "xx..",
        "x...",
    ],

    [
        'xx..xx',
        '...xx.',
        '.x....',
        'xxxx..',
        '..x...',
        'x....x'
    ]
]


@app.route('/', methods=["GET"])
def GET_maze_segment():
    height = request.args.get('height') or 7
    width = request.args.get('width') or 7

    letter_map = letter_maps[randint(0, len(letter_maps)-1)]

    maze = CustomMazeGenerator(
        height=height, width=width, letter_map=letter_map).create()
    print(maze.encode())

    response = jsonify({"geom": maze.encode()})
    response.headers["Cache-Control"] = 'no-store'

    return response, 200
