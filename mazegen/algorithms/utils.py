from ..cell import Cell
from .. import constants


def remove_wall(cur_cell: Cell, next_cell: Cell, direction: int) -> None:
    cur_cell.open_wall(direction)
    next_cell.open_wall(constants.OPPOSITE[direction])


def is_inside(x: int, y: int, width: int, height: int) -> bool:
    return (
        0 <= x < width and 0 <= y < height
    )
