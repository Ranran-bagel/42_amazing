from .exceptions import MazeGenerationError, PatternError
from .config import MazeConfig
from .algorithms.utils import is_inside, remove_wall
from .algorithms.dfs_algorithm import dfs
from .algorithms.kruskal_algorithm import kruskal
from .algorithms.prim_algorithm import prim
from .pathfinding import bfs, path_to_direction
from .cell import Cell
from . import constants
import random

FORTY_TWO_WIDTH = 7
FORTY_TWO_HEIGHT = 5

FORTY_TWO_PATTERN = (
    (0, 0),                 (4, 0), (5, 0), (6, 0),

    (0, 1),                                 (6, 1),

    (0, 2), (1, 2), (2, 2), (4, 2), (5, 2), (6, 2),

    (2, 3), (4, 3),

    (2, 4), (4, 4), (5, 4), (6, 4),
)


class MazeGenerator:
    def __init__(self, config: MazeConfig) -> None:
        self._entry = config.entry
        self._exit = config.exit
        self._width: int = config.width
        self._height: int = config.height
        self._is_perfect = config.perfect
        self._seed = config.seed
        self._output_file = config.output_file
        self.rng = random.Random(self._seed)
        self._algorithm = config.algorithm
        self.grid: list[list[Cell]] = [
            [Cell(x, y) for x in range(self._width)]
            for y in range(self._height)
        ]

    def reset_grid(self) -> None:
        self.grid = [
                    [Cell(x, y) for x in range(self._width)]
            for y in range(self._height)
        ]

    def _can_create_42(self) -> bool:
        return (
            self._width >= FORTY_TWO_WIDTH + 2
            and self._height >= FORTY_TWO_HEIGHT + 2
        )

    def _can_place_42_at(self, start_x: int, start_y: int) -> bool:
        for dx, dy in FORTY_TWO_PATTERN:
            x = start_x + dx
            y = start_y + dy

            if not (0 <= x < self._width and 0 <= y < self._height):
                return False
            if (x, y) == self._entry:
                return False
            if (x, y) == self._exit:
                return False
        return True

    def _place_42_at(self, start_x: int, start_y: int,) -> None:
        for dx, dy in FORTY_TWO_PATTERN:
            x = start_x + dx
            y = start_y + dy
            self.grid[y][x].blocked = True

    def _create_42(self) -> None:
        if not self._can_create_42():
            raise PatternError("Maze is too small for 42 pattern")

        start_x = (self._width - FORTY_TWO_WIDTH) // 2
        start_y = (self._height - FORTY_TWO_HEIGHT) // 2

        if self._can_place_42_at(start_x, start_y):
            self._place_42_at(start_x, start_y)
        else:
            valid_positions: list[tuple[int, int]] = []
            for y in range(1, self._height - FORTY_TWO_HEIGHT):
                for x in range(1, self._width - FORTY_TWO_WIDTH):
                    if self._can_place_42_at(x, y):
                        valid_positions.append((x, y))
            if not valid_positions:
                raise PatternError(
                    "No valid position available for 42 pattern"
                )
            start_x, start_y = self.rng.choice(valid_positions)
            self._place_42_at(start_x, start_y)

    def add_wall(self, cur_cell: Cell, next_cell: Cell, direction: int) -> None:
        cur_cell.close_wall(direction)
        next_cell.close_wall(constants.OPPOSITE[direction])

    def _is_open_3x3(self, start_x: int, start_y: int) -> bool:
        for y in range(start_y, start_y + 3):
            for x in range(start_x, start_x + 3):
                if self.grid[y][x].blocked:
                    return False

        for y in range(start_y, start_y + 3):
            for x in range(start_x, start_x + 2):
                if self.grid[y][x].has_wall(constants.EAST):
                    return False

        for y in range(start_y, start_y + 2):
            for x in range(start_x, start_x + 3):
                if self.grid[y][x].has_wall(constants.SOUTH):
                    return False

        return True

    def _has_open_3x3(self) -> bool:
        for y in range(self._height - 2):
            for x in range(self._width - 2):
                if self._is_open_3x3(x, y):
                    return True
        return False

    def _add_loops(self) -> None:
        candidates: list[tuple[Cell, Cell, int]] = []
        loops_added: int = 0
        for row in self.grid:
            for cell in row:
                x, y = cell.x, cell.y
                if is_inside(x + 1, y, self._width, self._height):
                    east_cell = self.grid[y][x + 1]
                else:
                    east_cell = None
                if is_inside(x, y + 1, self._width, self._height):
                    south_cell = self.grid[y + 1][x]
                else:
                    south_cell = None
                if cell.blocked:
                    continue
                if (east_cell
                    and not east_cell.blocked
                        and cell.has_wall(constants.EAST)):
                    candidates.append((cell, east_cell, constants.EAST))
                if (south_cell
                    and not south_cell.blocked
                        and cell.has_wall(constants.SOUTH)):
                    candidates.append((cell, south_cell, constants.SOUTH))

        target: int = max(1, len(candidates) // 10)
        self.rng.shuffle(candidates)
        for cell, next_cell, direction in candidates:
            if loops_added >= target:
                break
            remove_wall(cell, next_cell, direction)
            if self._has_open_3x3():
                self.add_wall(cell, next_cell, direction)
                continue
            loops_added += 1

    def generate(self) -> None:
        self.reset_grid()

        try:
            self._create_42()
        except PatternError as error:
            print(f"ERROR: {error}")

        if self._algorithm == "dfs":
            dfs(self.grid, self.rng)
        elif self._algorithm == "prim":
            prim(self.grid, self.rng)
        elif self._algorithm == "kruskal":
            kruskal(self.grid, self.rng)
        else:
            raise MazeGenerationError(
                f"Unsupported algorithm: {self._algorithm}"
            )

        if not self._is_perfect:
            self._add_loops()

    def output_mazefile(self) -> None:
        file_name: str = self._output_file
        try:
            with open(file_name, "w") as file:
                for row in self.grid:
                    for cell in row:
                        file.write(format(cell.walls, "X"))
                    file.write("\n")
                file.write("\n")
                file.write(f"{self._entry[0]}, {self._entry[1]}\n")
                file.write(f"{self._exit[0]}, {self._exit[1]}\n")
                path: list[tuple[int, int]] = bfs(
                    self.grid, self._entry, self._exit)
                file.write(path_to_direction(path))
        except PermissionError as error:
            raise MazeGenerationError(f"Permission denied: {
                                      file_name}") from error
        except OSError as error:
            raise MazeGenerationError(f"Cannot write maze file: {
                                      file_name}") from error
