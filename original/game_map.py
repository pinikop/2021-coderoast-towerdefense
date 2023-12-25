from typing import List

from game import BaseObject, GameObject


class Grid:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid: List[List[GameObject]] = [
            [BaseObject(i, j) for i in range(self.width)] for j in range(self.height)
        ]

    def get_object(self, i: int, j: int):
        return self.grid[i][j]

    def add_object(self, object: GameObject, i: int, j: int):
        self.grid[i][j] = object

    def remove_object(self, i: int, j: int):
        self.grid[i][j] = BaseObject(i, j)

    def update(self):
        """Updates the game"""
        for row in self.grid:
            for obj in row:
                obj.update()

    def paint(self, canvas):
        """Paints the game"""
        for row in self.grid:
            for obj in row:
                obj.paint(canvas)
