import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Tuple

from PIL import Image, ImageTk

from game import GameObject
from tiles import choose_tile_type


@dataclass
class Grid:
    values: List[List[int]]
    tile_size: Tuple[int, int]
    func: Callable

    def __post_init__(self):
        self.height = len(self.values)
        self.width = len(self.values[0])
        self.fill()

    def fill(self):
        self.grid = [
            [self.func(self.values, i, j, self.tile_size) for i in range(self.width)]
            for j in range(self.height)
        ]

    def get_object(self, i: int, j: int):
        return self.grid[j][i]

    def update(self):
        """Updates the game"""
        for row in self.grid:
            for obj in row:
                obj.update()

    def paint(self, image):
        """Paints the game"""
        for j, row in enumerate(self.grid):
            for i, obj in enumerate(row):
                obj.paint(image, i, j)


class Map(GameObject):
    def __init__(self, map_name: str, tile_size: Tuple[int, int]):
        self.tile_width = tile_size[0]
        self.tile_height = tile_size[1]
        self.map_name = map_name
        self.root_path = Path("./texts/mapTexts/")

        self.initialize()

    def initialize(self):
        self.create_grid()
        self.create_image()

    def read_map_file(self):
        with open(self.root_path / self.map_name, "r") as f:
            grid_values = [list(map(int, row.split())) for row in f]  # type: ignore
        return grid_values

    def create_image(self):
        image = Image.new(
            "RGBA",
            (self.tile_width * self.grid.width, self.tile_height * self.grid.height),
            (255, 255, 255, 255),
        )
        self.grid.paint(image)
        self.image = ImageTk.PhotoImage(image)

    def create_grid(self):
        values = self.read_map_file()
        self.grid = Grid(values, (self.tile_width, self.tile_height), choose_tile_type)

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
