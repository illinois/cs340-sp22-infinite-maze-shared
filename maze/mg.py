from maze.maze import Maze


class MazeGenerator:
    def __init__(self, num_rows=7, num_cols=7):
        self.height = num_rows
        self.width = num_cols
        self.maze = Maze(num_rows, num_cols)

    def create(self) -> Maze:
        return self.maze
