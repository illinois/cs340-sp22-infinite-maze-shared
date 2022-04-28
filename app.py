import requests
from flask import Flask, jsonify, render_template, request
from maze.maze import Maze
from servers import ServerManager

app = Flask(__name__)
server_manager = ServerManager('cs240-infinite-maze')


@app.route('/', methods=["GET"])
def GET_index():
    '''Route for "/" (frontend)'''
    return render_template("index.html")


@app.route('/generateSegment', methods=["GET"])
def gen_rand_maze_segment():
    '''Route for maze generation with random generator'''

    if not server_manager.has_servers():
        return 'No servers are available', 503

    mg_name = server_manager.select_random()
    print("Generator Selected: " + mg_name)
    return gen_maze_segment(mg_name)


@app.route('/generateSegment/<mg_name>', methods=['GET'])
def gen_maze_segment(mg_name: str):
    '''Route for maze generation with specific generator'''

    server = server_manager.find(mg_name)

    if not server:
        return 'Server not found', 404

    mg_url = server['url']

    if mg_url[-1] == '/':  # handle trailing slash
        mg_url = mg_url[:-1]

    try:
        r = requests.get(f'{mg_url}/generate', params=dict(request.args))
    except:
        server_manager.remove(mg_name) # Remove faulty server from DB
        return "", 500

    if r.status_code // 100 != 2:  # if not a 200-level response
        server_manager.remove(mg_name) # Remove faulty server from DB
        return 'Maze generator error', 500

    data = r.json()
    print(data)
    maze = Maze.decode(data['geom'])
    print(maze)
    maze = maze.add_boundary()
    data['geom'] = maze.encode()

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

    server = {
        'name': request.json['name'],
        'url': request.json['url'],
        'author': request.json['author'],
        'weight': new_weight
    }

    status, error_message = server_manager.insert(server)

    print(server_manager.servers)

    if status // 100 != 2:
        return jsonify({"error": error_message})

    server = server_manager.find(server['name'])

    return jsonify(server), status


@app.route('/servers', methods=['GET'])
def FindServers():
    servers = server_manager.servers
    return render_template('servers.html', data={"servers": servers})


@app.route('/listMG', methods=['GET'])
def list_maze_generators():
    '''Route to get list of maze generators'''
    servers = server_manager.servers
    return jsonify(servers), 200
