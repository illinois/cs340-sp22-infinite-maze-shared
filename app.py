import random
import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
available_MGs = {}

# lists of MG names and weights for random.choices
names = []
weights = []
def update_rng():
    '''Update `names` and `weights` variables'''
    global names, weights
    names = list(available_MGs.keys())
    weights = [mg['weight'] for mg in available_MGs.values()]

@app.route('/', methods=["GET"])
def GET_index():
    '''Route for "/" (frontend)'''
    return render_template("index.html")


@app.route('/generateSegment', methods=["GET"])
def gen_rand_maze_segment():
    # Zero-maze Debug Stub Code:
    # g1 = ["9aa2aac", "59aaaa4", "51aa8c5", "459a651", "553ac55", "559a655", "3638a26"]
    # g2 = ["988088c", "1000004", "1000004", "0000000", "1000004", "1000004", "3220226"]
    # return { "geom": g1 if random.random() < 0.1 else g2 }

    '''Route for maze generation with random generator'''
    if not available_MGs:
        return 'No maze generators available', 503
    
    # mg_name = random.choice(list(available_MGs.keys()))
    mg_name = random.choices(names, weights=weights)[0]
    return gen_maze_segment(mg_name)


@app.route('/generateSegment/<mg_name>', methods=['GET'])
def gen_maze_segment(mg_name: str):
    '''Route for maze generation with specific generator'''
    if mg_name not in available_MGs.keys():
        return 'Maze generator not found', 404
    
    mg_url = available_MGs[mg_name]['url']
    if mg_url[-1] == '/': # handle trailing slash
        mg_url = mg_url[:-1]
    r = requests.get(f'{mg_url}/generate', params=dict(request.args))
    
    if (r.status_code // 100) != 2: # if not a 200-level response
        return 'Maze generator error', 500
    return jsonify(r.json())


@app.route('/addMG', methods=['PUT'])
def add_maze_generator():
    '''Route to add a maze generator'''

    # Validate packet:
    for requiredKey in ['name', 'url', 'author']:
        if requiredKey not in request.json.keys():
            return f'Key "{requiredKey}" missing', 400

    if 'weight' in request.json.keys():
        new_weight = request.json['weight']
        if new_weight <= 0:
            return 'Weight cannot be 0 or negative', 400
    else:
        new_weight = 1

    available_MGs[request.json['name']] = {
        'name': request.json['name'],
        'url': request.json['url'],
        'author': request.json['author'],
        'weight': new_weight
    }

    update_rng()
    return 'OK', 200


@app.route('/servers', methods=['GET'])
def FindServers():
    return render_template('servers.html', data={"servers": available_MGs})


@app.route('/listMG', methods=['GET'])
def list_maze_generators():
    '''Route to get list of maze generators'''
    return jsonify(available_MGs), 200
