from os import environ
from flask import Flask, jsonify, redirect, render_template, request
from maze.maze import Maze
from servers import ServerManager
import json
import time
import requests
from datetime import datetime, timedelta
from global_maze import GlobalMaze
import random

FREE_SPACE_RADIUS = 10
ALLOW_DELETE_MAZE = True

STATUS_OK = 0
STATUS_BAD = 1

app = Flask(__name__)
server_manager = ServerManager('cs240-infinite-maze')

crumbs = {}
cache = {}
'''`{ (<mg_url>, <author>): (<expiry_datetime>, <data>) }`'''

maze_state = GlobalMaze()

MAZE_ERR_503 = ["9a8088c","5b02024","5b49494","0a02020","5b4d1e5","1e571e5","3a282a6"]

DEFAULT_MG_1 = ["9aa2aac", "59aaaa4", "51aa8c5",
                "459a651", "553ac55", "559a655", "3638a26"]

DEFAULT_MG_2 = ["988088c", "1000004", "1000004",
                "0000000", "1000004", "1000004", "3220226"]

user_color_choice = {}


@app.route('/', methods=["GET"])
def GET_index():
    '''Route for "/" (frontend)'''
    return render_template("index.html")


@app.route('/addUserColor/<user>/<color>', methods=["POST"])
def add_user_color(user, color):
    user_color_choice[user] = color
    return f"Added user color: {color}!", 200


@app.route('/<user>/generateSegment', methods=["GET"])
def gen_rand_maze_segment(user):
    '''Route for maze generation with random generator'''

    # get row and col
    row = 0
    col = 0

    if 'row' in request.args.keys():
        row = int(request.args['row'])
    if 'col' in request.args.keys():
        col = int(request.args['col'])

    old_segment = maze_state.get_state(row, col)
    if old_segment != None:  # segment already exists in maze state
        tmp = old_segment[0]
        tmp["color"] = old_segment[1]
        return jsonify(tmp), 200

    # If no MGs online, send the default one only
    if not server_manager.has_servers():
        print('No maze generators available')
        return jsonify({"geom": MAZE_ERR_503}), 200
        # return jsonify({"geom": DEFAULT_MG_1 if random.random() < 0.5 else DEFAULT_MG_2}), 200

    # scan free space
    free_space = []
    for coords in maze_state.get_free_space(row, col, FREE_SPACE_RADIUS):
        free_space.append(coords[0])
        free_space.append(coords[1])

    mg_name = server_manager.select_random()
    print("MG Selected: " + mg_name)

    output, status = gen_maze_segment(
        mg_name, data={'main': [row, col], 'free': free_space})

    if status // 100 != 2:
        # return output, status
        # RETRY DIFFERENT MAZE GENERATOR ON ERROR
        while status // 100 != 2:
            if not server_manager.has_servers():
                print('No maze generators available')
                return jsonify({"geom": MAZE_ERR_503}), 200
                # return jsonify({"geom": DEFAULT_MG_1 if random.random() < 0.5 else DEFAULT_MG_2}), 200

            mg_name = server_manager.select_random()
            print("MG Selected: " + mg_name)
            output, status = gen_maze_segment(
                mg_name, data={'main': [row, col], 'free': free_space})

    data = json.loads(output.data)
    # print(data)

    # intercept 'extern' key
    if 'extern' in data.keys():
        for key, val in data['extern'].items():
            # add external segments to maze_state
            r, c = [int(x) for x in key.split('_')]
            if maze_state.get_state(r, c) == None:
                maze_state.set_state(r, c, val, user_color_choice[user])

        # hide external segments from front-end
        del data['extern']

    maze_state.set_state(row, col, data, user_color_choice[user])

    server = server_manager.find(mg_name)
    prevCount = int(server['count']) if 'count' in server else 0
    server_manager.update(mg_name, {"count": prevCount + 1})

    return jsonify(data), 200


@app.route('/generateSegment/<mg_name>', methods=['GET'])
def gen_maze_segment(mg_name: str, data=None):
    '''Route for maze generation with specific generator'''

    server = server_manager.find(mg_name)

    if not server:
        return 'Server not found', 404

    mg_url = server['url']

    if mg_url[-1] == '/':  # handle trailing slash
        mg_url = mg_url[:-1]

    try:
        r = requests.get(f'{mg_url}/generate',
                         params=dict(request.args), json=data, timeout=1)

    except requests.exceptions.Timeout:
        message = 'Error: Timeout Error'
        server_manager.update(
            mg_name, {"status": STATUS_BAD, "message": message})
        return message, 500

    except requests.exceptions.TooManyRedirects:
        message = 'Error: Too Many Redirects'
        server_manager.update(
            mg_name, {"status": STATUS_BAD, "message": message})
        return message, 500

    except requests.exceptions.RequestException as e:
        message = 'Error: Request Exception'
        server_manager.update(
            mg_name, {"status": STATUS_BAD, "message": message})
        return message, 500

    # if not a 200-level response
    if r.status_code // 100 != 2:
        message = f'Error: {r.status_code}'
        server_manager.update(
            mg_name, {"status": STATUS_BAD, "message": message})
        return message, 500

    data = r.json()
    geom = data['geom']

    try:
        maze = Maze.decode(geom)

        if maze and maze.width % 7 != 0 or maze.height % 7 != 0:
            message = 'Maze has invalid dimensions'
            server_manager.update(
                mg_name, {"status": STATUS_BAD, "message": message})
            return message, 500

            # maze validation

        # force boundaries if single-unit segment
        if 'extern' not in data.keys():
            maze = maze.add_boundary()

        geom = maze.encode()
        print(f'GEOM: {geom}')
        data['geom'] = geom
    except:
        message = 'Failed to decode maze'
        server_manager.update(
            mg_name, {"status": STATUS_BAD, "message": message})
        return message, 500

    return jsonify(data), 200


@app.route('/addMG', methods=['PUT'])
def add_maze_generator():
    '''Route to add a maze generator'''

    data = request.json

    if not data:
        return 'Data is missing', 400

    if 'name' not in data:
        return 'Mg Name is missing', 400

    mg_name = data['name']

    if server_manager.find(mg_name) is not None:
        # update
        if not ALLOW_DELETE_MAZE:
            return "The current server settings does not allow MGs to be modified.", 401

        status, message = server_manager.update(mg_name, data)

        print(server_manager.servers)
        mg = server_manager.find(mg_name)
        print(mg)

        return jsonify({"message": message, mg_name: server_manager.find(mg_name)}), status

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

    server = {
        'name': request.json['name'],
        'url': request.json['url'],
        'author': request.json['author'],
        'weight': new_weight,
        'status': STATUS_OK,
        'message': '',
        'count': 0
    }

    # TODO: Test MG before adding

    status, error_message = server_manager.insert(server)

    print(server_manager.servers)

    if status // 100 != 2:
        return jsonify({"error": error_message}), status

    server = server_manager.find(server['name'])

    return jsonify(server), status


@app.route('/servers', methods=['GET'])
def FindServers():
    return render_template('servers.html', data={"servers": server_manager.servers})


@app.route('/listMG', methods=['GET'])
def list_maze_generators():
    '''Route to get list of maze generators'''
    servers = server_manager.servers
    return jsonify(servers), 200


@app.route('/mazeState', methods=['GET'])
def dump_maze_state():
    '''Dump global maze state internal JSON.'''
    return jsonify(maze_state.get_full_state()), 200


@app.route('/resetMaze', methods=['GET'])
def reset_maze_state():
    '''Reset global maze state.'''
    global maze_state
    if not maze_state.is_empty():
        maze_state.reset()
    return 'OK', 200


@app.route('/removeMG/<mg_name>', methods=['DELETE'])
def RemoveMG(mg_name):
    if not ALLOW_DELETE_MAZE:
        return "The current server settings does not allow MGs to be removed.", 401

    status, message = server_manager.remove(mg_name)
    return message, status


@app.route('/updateMG/<mg_name>', methods=['PUT'])
def UpdateMG(mg_name):
    if not ALLOW_DELETE_MAZE:
        return "The current server settings does not allow MGs to be modified.", 401

    data = request.get_json()

    if not data:
        return "data is missing", 400

    status, message = server_manager.update(mg_name, data)
    return message, status


@app.route('/log', methods=['GET'])
def logData():
    return jsonify({
        "names": server_manager.names,
        "weights": server_manager.weights,
        "servers": server_manager.servers
    }), 200


@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    '''Route for exchanging player location information'''
    # get POST data
    data = dict(request.form)
    # remove user id from data
    u = data.pop("user")
    # get current time
    now = int(time.time())
    # add a timestamp to the heartbeat data
    data["time"] = now
    # replace the user's entry in the breadcrumbs dict
    crumbs[u] = data
    # remove players that haven't sent a heartbeat in at least
    #  10 seconds
    for k in list(crumbs.keys()):
        age = now - crumbs[k]["time"]
        if age > 10:
            try:
                del crumbs[k]
            except KeyError:
                continue
    # return location information for all players
    return jsonify(crumbs), 200
