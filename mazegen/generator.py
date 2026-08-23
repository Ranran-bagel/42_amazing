from dataclasses import dataclass
import random

NORTH = 0b0001
EAST = 0b0010
SOUTH = 0b0100
WEST = 0b1000

ALL_WALLS = NORTH | EAST | SOUTH | WEST

DIRECTIONS = {
    NORTH: (0, -1),
    EAST: (1, 0),
    SOUTH: (0, 1),
    WEST: (-1, 0),
}

OPPOSITE = {
    NORTH: SOUTH,
    EAST: WEST,
    SOUTH: NORTH,
    WEST: EAST,
}

@dataclass
class Cell:
    x: int
    y: int
    walls: int = ALL_WALLS
    blocked: bool = False

    def has_wall(self, direction: int) -> bool:
        return bool(self.walls & direction)

    def open_wall(self, direction: int) -> None:
        self.walls &= ~direction

class MazeGenerator:
    def __init__(self, width: int, height: int, seed: int) -> None:
        self._width: int = width
        self._height: int = height
        self.visited = set[tuple[int, int]] = set()
        self.seed = seed
        self.rng = random.Random(self.seed)
        self.grid = [
            [Cell(x, y) for x in range(self._width)]
            for y in range(self._height)
        ]

    def is_inside(self, x: int, y: int) -> bool:
        return (
            0 <= x < self._width and 0 <= y < self._height
            )

    def get_unvisited_neighbors(self, cur_cell: Cell) -> list[Cell]:
        neighbors:list = list()
        x: int = cur_cell.x
        y: int = cur_cell.y
        for direction, (dx, dy) in DIRECTIONS.items():
            nx = x + dx
            ny = y + dy

            if not self.is_inside(nx, ny):
                continue
            if (nx, ny) in self.visited:
                continue
            if self.grid[ny][nx].blocked:
                continue
            neighbors.append((direction, nx, ny))
        return neighbors

    def generate(self) -> None: