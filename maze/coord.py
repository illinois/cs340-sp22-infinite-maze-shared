class Coord:
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def __add__(self, coord):
        return Coord(self.row + coord.row, self.col + coord.col)

    def __sub__(self, coord):
        return Coord(self.row - coord.row, self.col - coord.col)

    def __eq__(self, coord):
        return self.row == coord.row and self.col == coord.col
