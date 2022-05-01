from connection import Connection
from maze import *
import random


class ServerManager:
    def __init__(self, db_name):
        self.connection = Connection(db_name=db_name)  # database connection
        self.names = []  # list of server names for random.choices
        self.weights = []  # list of server weights for random.choices
        self.servers = {}  # cache: Maps server name to data
        self.load()
    
    def load(self):
        """Load existing servers from db and init internal caches. This function will erase existing cache."""

        # Reset data
        self.servers = {}
        self.names = []
        self.weights = []

        # Fetch all servers from db
        docs = self.connection.get_all_servers()

        for doc in docs:
            doc['_id'] = str(doc['_id'])
            self.servers[doc['name']] = doc
            self.names.append(doc['name'])
            self.weights.append(doc['weight'])

        print(self.servers)

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
            data['_id'] = str(data['_id'])  # store database ID
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

        del self.servers[name]

        for i in range(len(self.names)):
            if self.names[i] == name:
                self.names.pop(i)
                self.weights.pop(i)
                break

        return 200, ""

    def find(self, name):
        """Returns the MG data for given MG

        Args:
            name (str): Name of MG

        Returns:
            any: Returns MG or None if not found
        """
        if name not in self.servers:
            return None

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

        # Update caches

        for key in data:
            if key != 'name':
                self.servers[name][key] = data[key]
        
        if 'name' in data or 'weight' in data:
            for i in range(len(self.names)):
                if self.names[i] == name:
                    if 'weight' in data:
                        self.weights[i] = data['weight']
                    if 'name' in data:
                        self.names[i] = data['name']
                    break
                
        if 'name' in data:
            self.servers[name]['name'] = data['name']
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

    def select_from(self, choices) -> str:
        """Select random server from available ones and return it

        Returns:
            str: Name of server, or None if none
        """
        if not self.servers:
            return None

        mg_name = random.choices(
            population=choices,
            weights=[choice.weights for choice in choices],
            k=1,
        )[0]

        return mg_name

    def has_servers(self):
        """Returns True if there are any available servers, otherwise returns False.
        """
        return len(self.servers) > 0
