from http import server
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

            if 'status' not in doc:
                doc['status'] = 0

            # do not add unavilable MGs to list

            if doc['status'] == 0:
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

        update = {}

        # only update keys that have changed
        for key in data.keys():
            if self.servers[name].get(key,None) != data[key]:
                update[key] = data[key]            

        result = self.connection.update_server(self.servers[name]["_id"], update)

        print(result)

        if result.modified_count == 0:
            return 400, "No documents were updated"

        # Update caches

        # update all server keys except name, which is handled specially
        for key in data:
            if key != 'name':
                self.servers[name][key] = data[key]
        
        # If error resolved, add it back to list
        if self.servers[name]['status'] == 0 and name not in self.names:
            self.names.append(name)
            self.weights.append(self.servers[name]['weight'])
        
        # update names, weights list if name or weight has changed in the MG
        if 'name' in data or 'weight' in data:
            # find the MG in the names list
            # the index of the MG in the names and weights list is the same
            for i in range(len(self.names)):
                if self.names[i] == name:
                    if 'weight' in data:
                        self.weights[i] = data['weight']
                    if 'name' in data:
                        self.names[i] = data['name']
                    break
                
        # if server name changed, we need to copy the its data to a new key in the cache
        if 'name' in data and name != data['name']:
            self.servers[name]['name'] = data['name']
            self.servers[data['name']] = self.servers[name]
            # remove previous data
            del self.servers[name]
        
        # on failure remove this MG from names and weights list
        if 'status' in data and data['status'] != 0:
            for i in range(len(self.names)):
                if self.names[i] == name:
                    self.names.pop(i)
                    self.weights.pop(i)
                    print(f"Removed MG {name} from available servers")
                    break

        return 200, "Success"

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
        # The names list has available servers only, but servers dict has all servers
        return len(self.names) > 0
