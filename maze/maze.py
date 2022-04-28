from math import sqrt
from maze.coord import Coord
from maze.dir import dir_vec_arr, get_direction, NORTH, SOUTH, EAST, WEST


class Maze:
    def __init__(self, height, width) -> None:
        """Initialise a maze with <height> rows and <width> columns with no walls"""
        self.height = height
        self.width = width
        self.cells = [0] * (height * width)

    def can_travel(self, current: Coord, direction: int) -> bool:
        """Checks if we can travel from the cell at the current coord in the given direction"""
        if not self.is_valid(current):
            return False

        dx, dy = dir_vec_arr[direction]
        neighbor = current + Coord(dy, dx)

        if not self.is_valid(neighbor):
            return False

        return True

    def add_wall(self, current: Coord, direction: int) -> None:
        """Add a wall from the cell at current coord to the cell at the coord in the direction given, and vice versa"""
        if not self.is_valid(current):
            return

        self.cells[self.index(current)] |= (1 << direction)

        dx, dy = dir_vec_arr[direction]
        neighbor = current + Coord(dy, dx)
        reverse_direction = (direction + 2) % 4

        if not self.is_valid(neighbor):
            return

        self.cells[self.index(neighbor)] |= (1 << reverse_direction)

    def remove_wall(self, current: Coord, direction: int) -> None:
        """Remove the wall from the cell at current coord to the cell at the coord in the direction given, and vice versa"""
        if not self.is_valid(current):
            return

        dx, dy = dir_vec_arr[direction]
        neighbor = current + Coord(dy, dx)
        reverse_direction = (direction + 2) % 4

        if not self.is_valid(neighbor):
            return

        self.cells[self.index(current)] &= ~(1 << direction)
        self.cells[self.index(neighbor)] &= ~(1 << reverse_direction)

    def has_wall(self, first: Coord, second: Coord) -> bool:
        """Check if there exist wall between cells at given coord"""
        direction = get_direction(first, second)
        firstCell = self.cells[self.index(first)]

        if firstCell & (1 << direction) == 0:
            return False

        secondCell = self.cells[self.index(second)]
        reverse_direction = (direction + 2) % 4

        if secondCell & (1 << reverse_direction) == 0:
            return False

        return True

    def is_valid(self, coord: Coord) -> bool:
        """Checks if the cell given by coord is contained inside the maze."""
        return coord.row >= 0 and coord.row < self.height \
            and coord.col >= 0 and coord.col < self.width

    def size(self) -> int:
        """Return the size of the maze"""
        return self.width * self.height

    def index(self, coord: Coord) -> int:
        """Get the index of a cell in maze by given coord"""
        return coord.row * self.width + coord.col

    def coord(self, index: int) -> Coord:
        """Get the coord of the cell at given index in the array"""
        return Coord(index//self.width, index % self.width)

    def encode(self):
        """Encode the maze into a string array by encoding each cell with a single hexadecimal digit."""
        res = []

        for row in range(self.height):
            s = ''

            for col in range(self.width):
                s += hex(self.cells[row * self.width + col])[2:]

            res.append(s)

        return res

    def is_exterior(self, coord: Coord):
        """Checks if the given coord lies on the exterior part of the maze"""
        return coord.row == 0 or coord.row == self.height - 1 or coord.col == 0 or coord.col == self.width - 1

    def get_distance(self, u: Coord, v: Coord):
        """Returns Euclidean Distance between given coords"""
        return sqrt((v.row - u.row)**2 + (v.col - u.col)**2)

    def get_closest_edge_dir(self, coord: Coord):
        """Finds the direction in which the boundary of the maze is closest to the given coord"""
        north = self.get_distance(Coord(0, coord.col), coord)
        south = self.get_distance(Coord(self.height - 1, coord.col), coord)
        west = self.get_distance(Coord(coord.row, 0), coord)
        east = self.get_distance(Coord(coord.row, self.width - 1), coord)

        min_dist = min([north, south, west, east])

        if min_dist == north:
            return NORTH
        elif min_dist == south:
            return SOUTH
        elif min_dist == east:
            return EAST
        else:
            return WEST
    
    def add_boundary(self):
        """
        Surround the exterior of each 7x7 unit of the maze by walls but create an exit on the centre of each unit on each side.
        """
        for row in range(self.height):
            e = Coord(row, self.width - 1)
            w = Coord(row, 0)

            if row % 7 == 3:
                self.cells[self.index(w)] &= ~(1 << WEST)
                self.cells[self.index(e)] &= ~(1 << EAST)
            else:
                self.cells[self.index(w)] |= (1 << WEST)
                self.cells[self.index(e)] |= (1 << EAST)
            
        for col in range(self.width):
            n = Coord(0, col)
            s = Coord(self.height - 1, col)
            
            if col % 7 == 3:
                self.cells[self.index(n)] &= ~(1 << NORTH)
                self.cells[self.index(s)] &= ~(1 << SOUTH)
            else:
                self.cells[self.index(n)] |= (1 << NORTH)
                self.cells[self.index(s)] |= (1 << SOUTH)
        
        print(self.encode())

        return self

    def decode(geom):
        """Builds a maze from given geometry"""
        height = len(geom)
        width = len(geom[0])
        maze = Maze(height, width)
        for row in range(height):
            for col in range(width):
                maze.cells[maze.index(Coord(row,col))] = int(geom[row][col], 16)
        
        return maze
    

    def expand_maze_with_blank_space(self, new_height, new_width):
        if self.width > new_width or self.height > new_height:
            return self

        new_maze = Maze(new_height, new_width)
        x_off = (new_width - self.width) // 2
        y_off = (new_height - self.height) // 2

        for row in range(self.height):
            for col in range(self.width):
                inner_maze_idx = self.index(Coord(row, col))
                outer_maze_idx = new_maze.index(Coord(row + y_off, col + x_off))
                new_maze.cells[outer_maze_idx] = self.cells[inner_maze_idx]

                if row == 0 and self.cells[inner_maze_idx] & (1 << NORTH):
                    neighbor_coord = Coord(row + y_off - 1, col + x_off)
                    new_maze.add_wall(neighbor_coord, SOUTH)

                if col == 0 and self.cells[inner_maze_idx] & (1 << WEST):
                    neighbor_coord = Coord(row + y_off, col + x_off - 1)
                    new_maze.add_wall(neighbor_coord, EAST)

                if row == self.height-1 and self.cells[inner_maze_idx] & (1 << SOUTH):
                    neighbor_coord = Coord(row + y_off + 1, col + x_off)
                    new_maze.add_wall(neighbor_coord, NORTH)

                if col == self.width-1 and self.cells[inner_maze_idx] & (1 << EAST):
                    neighbor_coord = Coord(row + y_off, col + x_off + 1)
                    new_maze.add_wall(neighbor_coord, WEST)

        return new_maze
