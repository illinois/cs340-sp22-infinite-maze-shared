from numpy import insert
from connection import Connection
from maze import *
import random
# import validators

class ServerManager:
    def __init__(self, connection: Connection):
        self.names = [] # list of server names for random.choices
        self.weights = [] # list of server weights for random.choices
        self.servers = {} # cache: Maps server name to data 

        # Fetch all servers from db
        try:
            docs = self.connection.get_all_servers()

            for doc in docs:
                self.servers[doc['name']] = doc
                self.names.append(doc['name'])
                self.weights.append(float(doc['weight']))

            print(self.servers)
        except:
            raise Exception("Error loading servers from db")

    def insert(self, data: dict) -> tuple:
        """Inserts a server to Db and updates the names, weights and servers data of the class for new server.

        Args:
            data (dict): Server data must contain the name, url and author field. It can optionally have a weight between 0 and 1.

        Returns:
            tuple: (status code: int, error message: str)
            
            Status Codes
            -------------
            201: Success
            400: Invalid Data
            500: Database Error
            -------------
        """
        if 'name' not in data or 'url' not in data:
            return 400, "name or url invalid"

        # if not validators.url(data['url']):
        #     return 400, "url is invalid"

        if 'weight' not in data:
            data['weight'] = 1
        
        if data['weight'] < 0 or data['weight'] > 1:
            return 400, "weight is invalid"
        
        if self.servers and data['name'] in self.servers:
            return 400, "duplicate server name"

        result = self.connection.add_server(data)

        assert(len(self.names) == len(self.weights))

        if result:
            id = result.inserted_id
            data['_id'] = Connection.stringify_id(id)
            data['index'] = len(self.names) # index at which name and weight is stored in the arrays
            self.servers[data['name']] = data 
            self.names.append(data['name'])
            self.weights.append(data['weight'])

            return 201, ""

        return 500, "Database Error"

    def remove(self, name):
        if name not in self.servers:
            return "", 400
        
        self.connection.remove_server(self.servers['_id'])

        index = self.servers[name]
        del self.servers[name]
        self.names.pop(index)
        self.weights.pop(index)

        return "", 200

    def find(self, name):
        return self.servers[name]

    def update(self, name, data):
        """Update a server

        Args:
            name (str): name of the server
            data (dict): fields and values to update

        Returns:
            tuple: (status code, error message)
        """
        if name not in self.servers:
            return 400, "Server does not exist"

        for key in data:
            self.servers[name][key] = data[key]
        
        result = self.connection.update_server(self.servers[name]["_id"], data)

        index = self.servers[name]

        if 'weight' in data:
            self.weights[index] = data['weight']
        
        if 'name' in data:
            self.names[index] = data['name']
            self.servers[data['name']] = self.servers[name]
            del self.servers[name]

        if result.modified_count == 0:
            return 500, "Database Error"

        return 200, ""

    def select_random(self) -> dict:
        """Select random server from available ones and return it

        Returns:
            dict: server data, or None if there are none
        """
        if not self.servers:
            return None
            
        mg_name = random.choices(
            population = self.names,
            weights = self.weights,
            K = 1
        )

        return self.servers[mg_name]
