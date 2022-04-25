class GlobalMaze:
    '''Class to store global maze state and encapsulate logic'''
    __state = {}
    __is_empty = True
    
    def get_state(self, row: int, col: int):
        '''Returns maze segment data in current state for given coords'''
        subdict = self.__state.get(row)
        if subdict == None:
            return None
        return subdict.get(col)

    def set_state(self, row: int, col: int, data: dict):
        '''Modify current state of the maze'''
        subdict = self.__state.get(row)
        if subdict == None:
            self.__state[row] = {}
        self.__state[row][col] = data
        self.__is_empty = False
    
    def reset(self):
        '''Reset maze state'''
        if not self.__is_empty:
            self.__state = {}
            self.__is_empty = True

    def get_full_state(self):
        '''Get state of all segments'''
        return self.__state

    def is_empty(self):
        return self.__is_empty