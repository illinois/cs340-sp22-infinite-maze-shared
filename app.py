from flask import Flask, jsonify, render_template, request
from maze.maze import Maze
from servers import ServerManager
import json
from datetime import datetime, timedelta
import requests
from global_maze import GlobalMaze
from maze.possible_dimensions import possible_dimensions

FREE_SPACE_RADIUS = 10
ALLOW_DELETE_MAZE = True

app = Flask(__name__)
server_manager = ServerManager('cs240-infinite-maze')

cache = {}
'''`{ (<mg_url>, <author>): (<expiry_datetime>, <data>) }`'''

maze_state = GlobalMaze()


@app.route('/', methods=["GET"])
def GET_index():
    '''Route for "/" (frontend)'''
    return render_template("index.html")


@app.route('/generateSegment', methods=["GET"])
def gen_rand_maze_segment():
    '''Route for maze generation with random generator'''
    # Zero-maze Debug Stub Code:
    # g1 = ["9aa2aac", "59aaaa4", "51aa8c5", "459a651", "553ac55", "559a655", "3638a26"]
    # g2 = ["988088c", "1000004", "1000004", "0000000", "1000004", "1000004", "3220226"]
    # return { "geom": g1 if random.random() < 0.1 else g2 }

    # get row and col

    if len(request.args.keys()) == 0:
        # very first maze
    else:

        row = int(request.args["row"])
        col = int(request.args["col"])

        old_segment = maze_state.get_state(row, col)
        if old_segment != None: # segment already exists in maze state
            return old_segment, 200

        if not server_manager.has_servers():
            return 'No maze generators available', 503

        entrance_direction = int(request.args["entrance_direction"])

        possibilities_output = possible_dimensions(
                                                   maze_state.get_all_territories(),
                                                   entrance_direction,
                                                   row,
                                                   col,
                                                  )


        matching_servers = []

        for possibility in possibilities_output:

            for server in server_manager.get_all_servers():
                if (
                        (possibility.width is None or server["width"] == possibility.width)
                    and (possibility.height is None or server["height"] == possibility.height)
                   ):
                    matching_servers.append(server)

        if len(matching_servers) == 0:
            return 'No maze generators fit available space', 503


        r = requests.get(f'{server_manager.select_from(matching_servers)["url"]}/generate')
        r.raise_for_status()

        data = r.json()
        geom = data['geom']

        return {
                "geom" : geom,
                "xOffset" : possibility.x_offset,
                "yOffset" : possibility.y_offset,
               }, 200



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
        r = requests.get(f'{mg_url}/generate', params=dict(request.args), json=data)
    except:
        # Remove faulty server from DB
        # server_manager.remove(mg_name)  
        return "", 500

    if r.status_code // 100 != 2:  # if not a 200-level response
        # Remove faulty server from DB
        # server_manager.remove(mg_name)  
        return 'Maze generator error', 500

    data = r.json()
    geom = data['geom']

    # maze validation

    maze = Maze.decode(geom)
    new_width = maze.width
    new_height = maze.height

    if maze.width % 7 != 0:
        new_width = maze.width + 7 - (maze.width % 7)

    if maze.height % 7 != 0:
        new_height = maze.height + 7 - (maze.height % 7)

    # TODO: add_boundary
    # maze = maze.add_boundary()
    maze = maze.expand_maze_with_blank_space(
        new_height=new_height, new_width=new_width)
    # maze = maze.add_boundary()

    geom = maze.encode()
    print(f'GEOM: {geom}')
    data['geom'] = geom

    return jsonify(data), 200


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

    server = {
        'name': request.json['name'],
        'url': request.json['url'],
        'author': request.json['author'],
        'weight': new_weight,
        'width' : request.json['width'],
        'height' : request.json['heigh'],
    }

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


@app.route('/resetMaze', methods=['DELETE'])
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
