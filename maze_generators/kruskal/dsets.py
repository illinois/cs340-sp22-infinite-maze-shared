class DisjointSet:
    __data = []
    # negative value: root element, tree size is -value
    # positive value: index of parent

    def __init__(self, size: int):
        '''Create disjoint set object'''
        self.__data = [-1] * size

    def find(self, elem: int) -> int:
        '''Find root item'''
        if self.__data[elem] < 0:
            return elem
        output = self.find(self.__data[elem])
        self.__data[elem] = output # path compression
        return output

    def set_union(self, a: int, b: int) -> None:
        '''Merges 2 sets'''
        index_a = self.find(a)
        index_b = self.find(b)
        if index_a == index_b:
            return
        
        # connect smaller tree to bigger
        if self.__data[index_a] < self.__data[index_b]:
            # 2nd tree smaller, merge into 1st
            self.__data[index_a] += self.__data[index_b]
            self.__data[index_b] = index_a
        else:
            # 1st tree smaller, merge into 2nd
            self.__data[index_b] += self.__data[index_a]
            self.__data[index_a] = index_b

    def size(self, elem: int) -> int:
        return self.__data[self.find(elem)] * -1
