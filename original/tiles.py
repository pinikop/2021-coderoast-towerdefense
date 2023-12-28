from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image


@dataclass
class BaseTile:
    size: Optional[Tuple[int, int]] = None
    root_path: Path = Path("./images/blockImages/")
    tile_name: str = ""
    can_place: bool = False

    def __post_init__(self):
        face = Image.open(self.root_path / f"{self.tile_name}.png")
        if self.size is None:
            self.width = face.width
            self.height = face.width
        else:
            self.width, self.height = self.size
            face = face.resize(self.size)
        self.face = face

    def paste(self, image, x: int, y: int):
        image.paste(self.face, (x * self.width, y * self.height))


@dataclass
class GroundTile(BaseTile):
    tile_name: str = "NormalBlock"
    can_place: bool = True


@dataclass
class PathTile(BaseTile):
    tile_name: str = "PathBlock"


@dataclass
class WaterTile(BaseTile):
    tile_name: str = "WaterBlock"


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


def choose_tile_type(values, i, j, size):
    block_int = values[j][i]
    block_type = Tiles.from_value(block_int)
    return block_type(size)


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
