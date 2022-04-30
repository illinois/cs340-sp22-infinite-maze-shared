# Checks free space and inserts "foo" into 3x3 area

import json
import os
import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request

MG_NAME = 'debug_foo'

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


@app.route('/generate', methods=['GET'])
def generate():
    print('==Incoming JSON==')
    print(request.json)

    output = {}
    output['geom'] = ['foo']
    
    # get coords
    row = 0
    col = 0
    if 'row' in request.args.keys():
        row = int(request.args['row'])
    if 'col' in request.args.keys():
        col = int(request.args['col'])
    print(f'Coordinates: {(row, col)}')

    # scan free space and insert
    free_space = [x for x in zip(*[iter(request.json['free'])]*2)]
    output['extern'] = {}
    for r in range(row - 1, row + 2):
        for c in range(col - 1, col + 2):
            if (r, c) in free_space:
                output['extern'][f'{r}_{c}'] = {'geom': ['foo_2']}

    print('==Outgoing JSON==')
    print(output)
    return jsonify(output), 200
