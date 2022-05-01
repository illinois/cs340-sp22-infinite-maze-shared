from connection import Connection

class GlobalMaze:
    '''Class to store global maze state and encapsulate logic'''

    def __init__(self):
        self.__connection = Connection()
        self.__data_collection = self.__connection.db.maze_data
        self.__territory_collection = self.__connection.db.territories

    def get_state(self, row: int, col: int):
        '''Returns maze segment data in current state for given coords'''
        return self.__data_connection.find_one({"row" : row, "col": col}, projection={"_id" : False, "data" : True})

    def set_state(self, row: int, col: int, data: dict):
        '''Modify current state of the maze'''

        self.__data_connection.update_one({"row" : row, "col": col}, { "$set" : { "data" : data} })

    def reset(self):
        '''Reset maze state'''
        self.__data_connection.delete_many({})
        self.__territory_connection.delete_many({})

    def get_full_state(self):
        '''Get state of all segments'''
        return self.__data_connection.find({},
                                           projection={
                                                       "_id" : False,
                                                       "row" : True,
                                                       "col" : True,
                                                       "data": True,
                                                      }
                                          )

    def get_all_territories(self):
        '''Returns all territories at the moment'''
        return self.__territory_connection.find({}, projection)

    def set_territory(self, north, east, south, west):
        '''Add territory to the maze'''

        self.__data_connection.insert_one({
                                           "north" : north,
                                           "east" : east,
                                           "south" : south,
                                           "west" : west,
                                          })

    def is_empty(self) -> bool:
        '''Return `True` if no data is present, else return `False`'''
        return self.__data_collection.find_one({}, projection={"_id" : False}) is None
