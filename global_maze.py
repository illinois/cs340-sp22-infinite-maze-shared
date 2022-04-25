class GlobalMaze:
    '''Class to store global maze state and encapsulate logic'''
    __state = {}
    __is_empty = True
    
    def get_state(self, row: int, col: int):
        '''Returns maze segment data in current state for given coords'''
        return self.__state.get((row, col))

    def set_state(self, row: int, col: int, data: dict):
        '''Modify current state of the maze'''
        self.__state[(row, col)] = data
        self.__is_empty = False
    
    def reset(self):
        '''Reset maze state'''
        if not self.__is_empty:
            self.__state = {}
            self.__is_empty = True

    def get_full_state(self):
        '''Get state of all segments'''
        return self.__state

    def is_empty(self) -> bool:
        '''Return `True` if no data is present, else return `False`'''
        return self.__is_empty