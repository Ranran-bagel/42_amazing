from dataclasses import dataclass
from . import constants

@dataclass
class Cell:
    x: int
    y: int
    walls: int = constants.ALL_WALLS
    blocked: bool = False

    def has_wall(self, direction: int) -> bool:
        return bool(self.walls & direction)

    def open_wall(self, direction: int) -> None:
        self.walls &= ~direction

    def close_wall(self, direction: int) -> None:
        self.walls |= direction