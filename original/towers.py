from dataclasses import dataclass
from enum import Enum


@dataclass
class BaseShooter:
    name = "None"
    cost = 0


@dataclass
class ArrowShooter:
    name = "ArrowShooterTower"
    cost = 150


@dataclass
class BulletShooter:
    name = "BulletShooterTower"
    cost = 150


@dataclass
class TackShooter:
    name = "TackTower"
    cost = 150


@dataclass
class PowerShooter:
    name = "PowerTower"
    cost = 200


class Towers(Enum):
    NONE = BaseShooter
    ARROW_SHOOTER = ArrowShooter
    BULLET_SHOOTER = BulletShooter
    TACK_TOWER = TackShooter
    POWER_TOWER = PowerShooter

    @classmethod
    def from_value(cls, value):
        for item in cls:
            if item.value.name == value:
                return item
        raise ValueError(f"{value} is not a valid value for {cls.__name__}")
