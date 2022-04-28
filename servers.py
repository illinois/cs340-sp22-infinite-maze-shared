from connection import Connection
from maze import *
import random
# import validators


class ServerManager:
    def __init__(self, db_name):
        self.connection = Connection(db_name=db_name)  # database connection
        self.names = []  # list of server names for random.choices
        self.weights = []  # list of server weights for random.choices
        self.servers = {}  # cache: Maps server name to data

        # Fetch all servers from db
        docs = self.connection.get_all_servers()

        for doc in docs:
            self.servers[doc['name']] = doc
            self.names.append(doc['name'])
            self.weights.append(doc['weight'])

    def insert(self, data: dict) -> tuple:
        """Inserts a server to Db and updates the names, weights and servers data of the class for new server.

        Args:
            data (dict): Server data containing name, url, author and weight

        Returns:
            tuple: (status code: int, error message: str)

            Status Codes
            -------------
            201: Success
            400: User Error
            500: Database Error
            -------------
        """
        if self.servers and data['name'] in self.servers:
            return 400, "Duplicate Name Error"

        result = self.connection.add_server(data)

        assert(len(self.names) == len(self.weights))

        if result:
            id = result.inserted_id

            data['_id'] = Connection.stringify_id(id)  # store database ID

            # index at which name and weight is stored in the arrays
            data['index'] = len(self.names)

            self.servers[data['name']] = data
            self.names.append(data['name'])
            self.weights.append(data['weight'])

            return 201, ""

        return 500, "Database Error"

    def remove(self, name):
        """Removes a server with given name

        Args:
            name (str): Name of server

        Returns:
            tuple: (status code, error message)
        """
        if name not in self.servers:
            return 400, ""

        self.connection.remove_server(self.servers[name]['_id'])

        # Update cache

        index = self.servers[name]['index']
        del self.servers[name]
        self.names.pop(index)
        self.weights.pop(index)

        return 200, ""

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

        result = self.connection.update_server(self.servers[name]["_id"], data)

        if result.modified_count == 0:
            return 500, "Database Error"

        # Update cache

        for key in data:
            self.servers[name][key] = data[key]

        index = self.servers[name]['index']

        if 'weight' in data:
            self.weights[index] = data['weight']

        if 'name' in data:
            self.names[index] = data['name']
            self.servers[data['name']] = self.servers[name]
            del self.servers[name]

        return 200, ""

    def select_random(self) -> str:
        """Select random server from available ones and return it

        Returns:
            str: Name of server, or None if none
        """
        if not self.servers:
            return None

        mg_name = random.choices(
            population=self.names,
            weights=self.weights,
            k=1
        )[0]

        return mg_name

    def has_servers(self):
        """Returns True if there are any available servers, otherwise returns False.
        """
        return len(self.servers) > 0
