import os
import sys
import inspect

current_dir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
parent_dir = os.path.dirname(parent_dir)
sys.path.insert(0, parent_dir)

from maze import *
from random import randint


class CustomMazeGenerator(MazeGenerator):
    def __init__(self, height=7, width=7, letter_map=[], space_char='.', boundary_char='x'):
        self.letter_map = letter_map
        self.space_char = space_char
        self.boundary_char = boundary_char

        self.letter_height = len(letter_map)
        self.letter_width = len(letter_map[0])

        if height < self.letter_height:
            height = self.letter_height

        if width < self.letter_width:
            width = self.letter_width

        max_x_offset = height - self.letter_height
        max_y_offset = width - self.letter_width

        self.y_offset = randint(0, max_y_offset)
        self.x_offset = randint(0, max_x_offset)

        super().__init__(height, width)

    def create(self):
        for i in range(self.width * self.height):
            self.maze.cells[i] = 0

        for row in range(self.letter_height):
            for col in range(self.letter_width):
                if self.letter_map[row][col] == self.space_char:
                    continue

                maze_x = (self.x_offset+col)
                maze_y = (self.y_offset+row)

                current = Coord(maze_y, maze_x)

                for i in range(4):
                    dx, dy = dir_vec_arr[i]

                    x = col + dx
                    y = row + dy

                    if x < 0 or x >= self.letter_width or y < 0 or y >= self.letter_height:
                        continue
                    elif self.letter_map[y][x] == self.boundary_char:
                        self.maze.remove_wall(current, i)
                    else:
                        self.maze.add_wall(current, i)

        return self.maze


if __name__ == '__main__':
    letter_map = [
        'x...',
        'x...',
        'x...',
        'x...',
        'xxxx',
    ]

    maze = CustomMazeGenerator(
        height=7, width=7, letter_map=letter_map).create()

    print(maze.encode())
