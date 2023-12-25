import tkinter as tk
from itertools import product
from typing import List

from PIL import Image, ImageTk

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


# class Map(GameObject):
#     def __init__(self, grid, map_name: str, block_width: int, block_height: int):
#         self.block_width = block_width
#         self.block_height = block_height
#         self.grid = grid
#         self.map_name = map_name
#         self.image = self.load_map()

#     def read_map_file(self):
#         map_file = open(f"texts/mapTexts/{self.map_name}.txt", "r")
#         with open(map_file, "r") as mf:
#             map_str = map_file.read()
#         return map_str

#     def parse_map_vector(self, map_str):
#         return list(map(int, map_str.split()))

#     def fill_grid(self, grid_values):
#         for i, j in product(range(self.grid.width), range(self.grid.height)):
#             block_int = grid_values[self.grid.width * j + i]
#             # @TODO: move to blocks file, function(block_int) ->
#             match block_int:
#                 case 0:
#                     block_type = NormalBlock
#                 case 1:
#                     block_type = PathBlock
#                 case 2:
#                     block_type = WaterBlock
#             ################

#             self.grid.add_object(
#                 block_type(
#                     i * self.block_width + self.block_width / 2,
#                     j * self.block_height + self.block_height / 2,
#                     block_int,
#                     i,
#                     j,
#                 ),
#                 i,
#                 j,
#             )

#     def create_image(self):
#         image = Image.new(
#             "RGBA",
#             (self.block_width * self.grid.width, self.block_width * self.grid.width),
#             (255, 255, 255, 255),
#         )
#         self.grid.paint(image)
#         image = ImageTk.PhotoImage(image)
#         return image

#     def load_map(self):
#         map_str = self.read_map_file()
#         grid_values = self.parse_map_vector(map_str)
#         image = self.fill_grid(grid_values)
#         return image

#     def paint(self, canvas):
#         canvas.create_image(0, 0, image=self.image, anchor=tk.NW)
