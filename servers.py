from http import server
from connection import Connection
from maze import *
import random


class ServerManager:
    def __init__(self, db_name):
        self.connection = Connection(db_name=db_name)  # database connection
        self.mids = []  # list of server names for random.choices
        self.weights = []  # list of server weights for random.choices
        self.serversByID = {}  # cache: Maps server name to data
        self.load()
    
    def load(self):
        """Load existing servers from db and init internal caches. This function will erase existing cache."""

        # Reset data
        self.serversByID = {}
        self.mids = []
        self.weights = []

        # Fetch all servers from db
        docs = self.connection.get_all_servers()

        for doc in docs:
            mid = doc['_id'] = str(doc['_id'])
            self.serversByID[mid] = doc

            if 'status' not in doc:
                doc['status'] = 0

            # do not add unavilable MGs to list

            if doc['status'] == 0:
                self.mids.append(doc['_id'])
                self.weights.append(doc['weight'])

        print(self.serversByID)

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
        # if self.servers and data['name'] in self.servers:
        #     return 400, "Duplicate Name Error"

        result = self.connection.add_server(data)

        assert(len(self.mids) == len(self.weights))

        if result:
            mid = data['_id'] = str(data['_id'])  # store database ID
            self.serversByID[mid] = data
            self.mids.append(mid)
            self.weights.append(data['weight'])

            return data

        return None

    def remove(self, mid):
        """Removes a server with given name

        Args:
            name (str): Name of server

        Returns:
            tuple: (status code, error message)
        """
        if mid not in self.serversByID:
            return 400, ""

        self.connection.remove_server(mid)

        # Update cache

        del self.serversByID[mid]

        for i in range(len(self.mids)):
            if self.mids[i] == mid:
                self.mids.pop(i)
                self.weights.pop(i)
                break

        return 200, ""

    def find_by_id(self, mid):
        if mid in self.serversByID:
            return self.serversByID[mid]
        
        return None

    def find_by_url(self, url):
        for key in self.serversByID:
            if self.serversByID[key]["url"] == url:
                return self.serversByID[key]
        
        return None

    def update(self, mid, data):
        """Update a server

        Args:
            name (str): name of the server
            data (dict): fields and values to update

        Returns:
            tuple: (status code, error message)
        """
        server = self.find_by_id(mid)
        if server == None:
            return 400, "Server does not exist"

        update = {}

        # only update keys that have changed
        for key in data.keys():
            if server.get(key, None) != data[key]:
                update[key] = data[key]            

        result = self.connection.update_server(mid, update)

        print(result)

        if result.modified_count == 0:
            return 400, "No documents were updated"

        # Update caches

        # update all server keys except name, which is handled specially
        for key in data:
            if key != 'name':
                self.serversByID[mid][key] = data[key]
        
        # If error resolved, add it back to list
        if self.serversByID[mid]['status'] == 0 and mid not in self.mids:
            self.mids.append(mid)
            self.weights.append(self.serversByID[mid]['weight'])
        
        # update names, weights list if name or weight has changed in the MG
        
        # TODO: Weights are always now fixed to `1`, this code was not fully refactored:
        # if 'mid' in data or 'weight' in data:
        #     # find the MG in the names list
        #     # the index of the MG in the names and weights list is the same
        #     for i in range(len(self.mids)):
        #         if self.mids[i] == mid:
        #             if 'weight' in data:
        #                 self.weights[i] = data['weight']
        #             if 'mid' in data:
        #                 self.mids[i] = mid
        #             break
                
        # if server name changed, we need to copy the its data to a new key in the cache
        # if 'name' in data and name != data['name']:
        #     self.servers[name]['name'] = data['name']
        #     self.servers[data['name']] = self.servers[name]
        #     # remove previous data
        #     del self.servers[name]
        
        # on failure remove this MG from names and weights list
        if 'status' in data and data['status'] != 0:
            for i in range(len(self.mids)):
                if self.mids[i] == mid:
                    self.mids.pop(i)
                    self.weights.pop(i)
                    print(f"Removed MG {mid} from available servers")
                    break

        return 200, "Success"

    def select_random(self) -> str:
        """Select random server from available ones and return it

        Returns:
            str: Name of server, or None if none
        """
        if not self.serversByID:
            return None

        mid = random.choices(
            population=self.mids,
            weights=self.weights,
            k=1
        )[0]

        return mid

    # def get_mid_from_name(self, name) -> str:
    #     return self.servers[name]["_id"]

    def has_servers(self):
        """Returns True if there are any available servers, otherwise returns False.
        """
        # The names list has available servers only, but servers dict has all servers
        return len(self.mids) > 0
