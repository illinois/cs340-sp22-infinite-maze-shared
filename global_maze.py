from connection import Connection

class GlobalMaze:
    '''Class to store global maze state and encapsulate logic'''
    __state = {}
    __is_empty = True
    __collection = 'mazes'
    __segments = 0
    __uid_segments = {}
    __in_init = True

    def __init__(self):
        self.__connection = Connection()

        mazes = self.__connection.db[GlobalMaze.__collection].find({})

        print('Loading Global Maze from db...')
        if mazes:
            for maze in mazes:
                print(maze)
                row = maze['row']
                col = maze['col']
                data = maze['data']
                color = maze['color']
                if 'uid' in maze: uid = maze['uid']
                else:             uid = "???"
                self.set_state(row, col, data, color, uid)
        
        self.__in_init = False

    def get_state(self, row: int, col: int):
        '''Returns maze segment data in current state for given coords'''
        return self.__state.get((row, col))

    def set_state(self, row: int, col: int, data: dict, color, uid):
        '''Modify current state of the maze'''
        print(f"DATA : {data}")
        self.__state[(row, col)] = (data, color)
        self.__is_empty = False

        # Track segments generated:
        self.__segments += 1
        if uid not in self.__uid_segments:
            self.__uid_segments[uid] = 0
        self.__uid_segments[uid] += 1

        if not self.__in_init:
            print(f"[GlobalMaze::set_state]: Added ({row}, {col}) -> {data}, color={color}")

            self.__connection.db[GlobalMaze.__collection].insert_one({
                'row': row,
                'col': col,
                'data': data,
                'color': color,
                'uid': uid,
            })

    def get_size(self):
        return self.__segments

    def get_segments_by_uid(self, uid):
        if uid not in self.__uid_segments:
            return 0
        else:
            return self.__uid_segments[uid]

    def reset(self):
        '''Reset maze state'''
        if not self.__is_empty:
            self.__state = {}
            self.__is_empty = True

            self.__connection.db[GlobalMaze.__collection].delete_many({})

    def get_full_state(self):
        '''Get state of all segments'''
        output = {}
        for key, val in self.__state.items():
            output[f'{key[0]}_{key[1]}'] = val
        return output

    def is_empty(self) -> bool:
        '''Return `True` if no data is present, else return `False`'''
        return self.__is_empty

    def get_free_space(self, row: int, col: int, radius: int) -> set:
        '''Return set of free spaces in given radius centered on given coords'''
        output = set()
        for r in range(row - radius, row + radius + 1):
            for c in range(col - radius, col + radius + 1):
                if (r, c) not in self.__state.keys():
                    output.add((r, c))
        return output