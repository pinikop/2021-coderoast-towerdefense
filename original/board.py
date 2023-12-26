import tkinter as tk
from dataclasses import dataclass
from itertools import product
from pathlib import Path
from typing import List

from PIL import Image, ImageTk

from game import BaseObject, GameObject
from tiles import Tiles


@dataclass
class Grid:
    width: int
    height: int

    def __post_init__(self):
        self.grid: List[List[GameObject]] = [
            [BaseObject(i, j) for i in range(self.width)] for j in range(self.height)
        ]

    def get_object(self, i: int, j: int):
        return self.grid[j][i]

    def add_object(self, obj: GameObject, i: int, j: int):
        self.grid[j][i] = obj

    def remove_object(self, i: int, j: int):
        self.grid[j][i] = BaseObject(j, i)

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


class Map(GameObject):
    def __init__(self, map_name: str, tile_width: int, tile_height: int):
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.map_name = map_name
        self.root_path = Path("./texts/mapTexts/")

        self.initialize()

    def initialize(self):
        self.grid_values = self.read_map_file()
        self.grid_width = len(self.grid_values[0])
        self.grid_height = len(self.grid_values)
        self.grid = Grid(self.grid_width, self.grid_height)
        self.image = self.load_map()

    def read_map_file(self):
        with open(self.root_path / self.map_name, "r") as f:
            grid_values = [list(map(int, row.split())) for row in f]
        return grid_values

    def fill_grid(self):
        for j, i in product(range(self.grid_height), range(self.grid_width)):
            block_int = self.grid_values[j][i]
            block_type = Tiles.from_value(block_int)

            self.grid.add_object(
                block_type(i * self.tile_width, j * self.tile_height), i, j
            )

    def create_image(self):
        image = Image.new(
            "RGBA",
            (self.tile_width * self.grid.width, self.tile_height * self.grid.height),
            (255, 255, 255, 255),
        )
        self.grid.paint(image)
        image = ImageTk.PhotoImage(image)
        return image

    def load_map(self):
        self.fill_grid()
        image = self.create_image()
        return image

    def paint(self, canvas):
        canvas.create_image(0, 0, image=self.image, anchor=tk.NW)


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
