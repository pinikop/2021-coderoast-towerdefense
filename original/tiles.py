from enum import Enum
from pathlib import Path

from PIL import Image

from game import GameObject


class BaseTile(GameObject):
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.root_path = Path("./images/blockImages/")
        self.tile_name = ""

    @property
    def tile(self):
        return Image.open(self.root_path / f"{self.tile_name}.png")

    def paint(self, canvas):
        canvas.paste(self.tile, (self.x, self.y))


class GroundTile(BaseTile):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.tile_name = "NormalBlock"


class PathTile(BaseTile):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.tile_name = "PathBlock"
        self.can_place = False


class WaterTile(BaseTile):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.tile_name = "WaterBlock"
        self.can_place = False


class Tiles(Enum):
    NORMAL = (0, GroundTile)
    PATH = (1, PathTile)
    WATER = (2, WaterTile)

    def __init__(self, idx, tile_type):
        self.idx = idx
        self.tile_type = tile_type

    @classmethod
    def from_value(cls, value):
        for item in cls:
            if item.idx == value:
                return item.tile_type
        raise ValueError(f"{value} is not a valid value for {cls.__name__}")


# def hovered_over(self, click, game):
#     if click:
#         global TOWER_GRID
#         global MONEY
#         if TOWER_GRID[self.grid_x][self.grid_y]:
#             if game.tower == Towers.NONE:
#                 TOWER_GRID[self.grid_x][self.grid_y].clicked = True
#                 global DISPLAY_TOWER
#                 DISPLAY_TOWER = TOWER_GRID[self.grid_x][self.grid_y]
#                 game.info_board.display_specific()
#         elif (
#             game.tower != Towers.NONE
#             and self.can_place == True
#             and MONEY >= TowerCost[game.tower]
#         ):
#             self.towerType = game.tower
#             TOWER_GRID[self.grid_x][self.grid_y] = self.towerType(
#                 self.x, self.y, self.grid_x, self.grid_y
#             )
#             MONEY -= TowerCost[game.tower]
