import json
import os
import random
import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request

from dsets import DisjointSet

MG_NAME = 'kruskal'
SIZE = 7

# load config file
with open('../config.json', 'r') as f:
    config = json.load(f)
MAIN_URL = config['main_url']
MAIN_PORT = config['main_port']

app = Flask(__name__)

# add self to middleware
load_dotenv()
port = int(os.getenv('FLASK_RUN_PORT'))
data = {'name': MG_NAME, 'url': f'{MAIN_URL}:{port}', 'author': config['author']}
if 'RNG_WEIGHT' in os.environ:
    weight = float(os.getenv('RNG_WEIGHT'))
    data['weight'] = weight
requests.put(f'{MAIN_URL}:{MAIN_PORT}/addMG', data=json.dumps(data), headers={'Content-Type': 'application/json'})

def compress_maze(dimensions: tuple, h_walls: list, v_walls: list) -> list:
    '''Compress maze data into format required for front-end'''
    output = []
    for row in range(dimensions[0]):
        row_string = ''
        for col in range(dimensions[1]):
            value = 0
            # check each wall
            if h_walls[row][col]:
                value += 2 ** 3
            if v_walls[row][col + 1]:
                value += 2 ** 2
            if h_walls[row + 1][col]:
                value += 2
            if v_walls[row][col]:
                value += 1
            row_string += hex(value)[2:]
        output.append(row_string)
    return output

def get_index(x: int, y: int) -> int:
    '''Helper function to map 2d coords to 1d index'''
    return y * SIZE + x

edges = [] # (x, y, direction)
           # direction: 0 = down, 1 = right
# add horizontal edges
for i in range(SIZE - 1):
    for j in range(SIZE):
        edges.append((i, j, 0))
# add vertical edges
for i in range(SIZE):
    for j in range(SIZE - 1):
        edges.append((i, j, 1))

@app.route('/generate', methods=['GET'])
def generate():
    print(request.json)

    dimensions = (SIZE, SIZE)
    h_walls = [[1 for _ in range(SIZE)] for _ in range(SIZE + 1)]
    v_walls = [[1 for _ in range(SIZE + 1)] for _ in range(SIZE)]

    dsets = DisjointSet(SIZE ** 2)

    random.shuffle(edges)

    for edge in edges:
        if edge[2] == 0: # down
            index_1 = get_index(edge[0], edge[1])
            index_2 = get_index(edge[0] + 1, edge[1])
            # ensure no cycle
            if dsets.find(index_1) == dsets.find(index_2):
                continue
            h_walls[edge[0] + 1][edge[1]] = 0
            dsets.set_union(dsets.find(index_1), dsets.find(index_2))
        else: # right
            index_1 = get_index(edge[0], edge[1])
            index_2 = get_index(edge[0], edge[1] + 1)
            # ensure no cycle
            if dsets.find(index_1) == dsets.find(index_2):
                continue
            v_walls[edge[0]][edge[1] + 1] = 0
            dsets.set_union(dsets.find(index_1), dsets.find(index_2))

    # remove entrances and exits
    midpoint = int((SIZE - 1) / 2)
    h_walls[0][midpoint] = 0
    h_walls[-1][midpoint] = 0
    v_walls[midpoint][0] = 0
    v_walls[midpoint][-1] = 0

    output = {}
    output['geom'] = compress_maze(dimensions, h_walls, v_walls)
    return jsonify(output), 200
