from random import randint
from flask import Flask, jsonify
import os
import sys
import inspect
from .custom_mg import CustomMazeGenerator

current_dir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
parent_dir = os.path.dirname(parent_dir)
sys.path.insert(0, parent_dir)

from maze import *
from random import shuffle

app = Flask(__name__)

Letter_0 = [
    '.......',
    '.......',
    '.......',
    '.......',
    '.......',
    '.......',
    '.......',
]

Letter_1 = [
    '.......',
    '.......',
    '.xxxxx.',
    '.......',
    '.xxxxx.',
    '.......',
    '.......',
]

letter_maps = [
    Letter_0,
    Letter_1
]


def makeSolvableMaze(maze: Maze) -> Maze:
    dset = DSet(maze.width * maze.height)

    for i in range(maze.width * maze.height):
        coord = maze.coord(i)
        row = coord.row
        col = coord.col

        for dir in range(4):
            dx, dy = dir_vec_arr[dir]

            if not maze.is_valid(Coord(row + dy, col + dx)):
                continue

            if not maze.has_wall(Coord(row, col), Coord(row + dy, col + dx)):
                dset.union(i, maze.index(Coord(row + dy, col + dx)))

    # Remove walls till maze is connected
    while dset.size(0) < maze.size():
        currentIndex = randint(0, maze.size() - 1)
        currentCoord = maze.coord(currentIndex)

        dirs = [i for i in dir_vec_arr]
        shuffle(dirs)

        for dir in dirs:
            dx = dir[0]
            dy = dir[1]

            neighborCoord = Coord(
                currentCoord.row + dy, currentCoord.col + dx)

            if not maze.is_valid(neighborCoord):
                continue

            neighborIndex = maze.index(neighborCoord)

            if dset.find(currentIndex) == dset.find(neighborIndex):
                continue

            dset.union(currentIndex, neighborIndex)

            dir = get_direction(currentCoord, neighborCoord)
            maze.remove_wall(currentCoord, dir)

            break
    
    return maze

@app.route('/generate', methods=["GET"])
def GET_maze_segment():
    selected_map = randint(0, len(letter_maps)-1)
    print("Selected map: " + str(selected_map))
    letter_map = letter_maps[selected_map]

    maze = CustomMazeGenerator(7, 7, letter_map).create()

    maze = maze.expand_maze_with_blank_space(7,7)
    maze = maze.add_boundary()

    maze = makeSolvableMaze(maze)
    
    response = jsonify({"geom": maze.encode()})
    response.headers["Cache-Control"] = 'no-store'
    return response, 200
