from pymongo import MongoClient
from bson.objectid import ObjectId

HOST = 'localhost'
PORT = 27017
DB_NAME = 'cs240-infinite-maze'

server_keys = ['name', 'url', 'author', 'weight']


def stringify_id(document):
    document["_id"] = str(document["_id"])
    return document


class Connection:
    def __init__(self, host=HOST, port=PORT, db_name=DB_NAME):
        try:
            self.mongo = MongoClient(host, port)
            self.db = self.mongo[db_name]
            self.alive = True
        except:
            self.alive = False
            self.mongo.close()
            print("Could not connect to the database!")
            exit(1)

    def __del__(self):
        if self.mongo is not None:
            self.mongo.close()

    def put_server(self, data):
        assert('name' in data)

        if not self.alive:
            return False

        exists = self.db.servers.find_one({"name": data["name"]})

        if not exists:
            if self.db.servers.insert_one(data):
                return "Success", 200
            else:
                return "Database Error", 500

        update = {}

        for key in server_keys:
            if key in data:
                if exists[key] != data[key]:
                    update[key] = data[key]

        if update:
            result = self.db.servers.update_one({"_id": ObjectId(exists["_id"])}, {"$set": update})
            if result.modified_count == 1:
                return "Updated", 200
        
        return "", 200

    def get_server(self, name):
        if not self.alive:
            return None

        found = self.db.servers.find_one({"name": name})

        if found:
            found = stringify_id(found)
            return found

        return None

    def get_all_servers(self):
        result = self.db.servers.find({})

        if result:
            result = list(result)
            for server in result:
                server = stringify_id(server)
            return result
        else:
            return []
