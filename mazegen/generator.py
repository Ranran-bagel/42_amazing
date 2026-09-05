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
            if (
                not self._is_perfect
                and (self._width // 2, self._height // 2) == (x, y)
            ):
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

    def add_wall(
            self,
            cur_cell: Cell,
            next_cell: Cell,
            direction: int
            ) -> None:
        cur_cell.close_wall(direction)
        next_cell.close_wall(constants.OPPOSITE[direction])

    def degree(self, cell: Cell) -> int:
        count: int = 0
        for derection in constants.DIRECTIONS:
            if not cell.has_wall(derection):
                count += 1
        return count

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

    def find_dead_ends(self) -> list[Cell]:
        dead_ends: list[Cell] = []
        for row in self.grid:
            for cell in row:
                if cell.blocked:
                    continue
                if self.degree(cell) == 1:
                    dead_ends.append(cell)
        return dead_ends

    def find_closed_neighbors(
            self,
            cell: Cell,
            x: int,
            y: int,
            ) -> list[tuple[int, int, int]]:
        neighbors: list[tuple[int, int, int]] = []
        for direction, (dx, dy) in constants.DIRECTIONS.items():
            nx = x + dx
            ny = y + dy
            if not is_inside(
                    nx,
                    ny,
                    self._width,
                    self._height
                    ):
                continue
            if self.grid[ny][nx].blocked:
                continue
            if not cell.has_wall(direction):
                continue
            neighbors.append((direction, nx, ny))
        return neighbors

    def count_tolerated_dead_ends(self) -> int:
        count = 0
        for cell in self.find_dead_ends():
            closed_neighbors = self.find_closed_neighbors(
                cell,
                cell.x,
                cell.y,
            )
            if not closed_neighbors:
                count += 1

        return count

    def braid_maze(self) -> bool:
        tolerated_dead_ends: int = self.count_tolerated_dead_ends()
        while True:
            dead_ends: list[Cell] = self.find_dead_ends()
            if len(dead_ends) <= tolerated_dead_ends:
                return True
            self.rng.shuffle(dead_ends)
            progress: bool = False
            for cell in dead_ends:
                if self.degree(cell) != 1:
                    continue
                neighbors: list[
                    tuple[int, int, int]
                    ] = self.find_closed_neighbors(
                        cell,
                        cell.x,
                        cell.y,
                        )
                self.rng.shuffle(neighbors)
                for direction, nx, ny in neighbors:
                    neighbor: Cell = self.grid[ny][nx]
                    remove_wall(cell, neighbor, direction)
                    if self._has_open_3x3():
                        self.add_wall(cell, self.grid[ny][nx], direction)
                        continue
                    progress = True
                    break

            if not progress:
                return len(dead_ends) <= tolerated_dead_ends

    def count_loops(self) -> int:
        vertices = 0
        edges = 0

        for row in self.grid:
            for cell in row:
                if cell.blocked:
                    continue
                vertices += 1
                if (
                    cell.x + 1 < self._width
                    and not self.grid[cell.y][cell.x + 1].blocked
                    and not cell.has_wall(constants.EAST)
                ):
                    edges += 1
                if (
                    cell.y + 1 < self._height
                    and not self.grid[cell.y + 1][cell.x].blocked
                    and not cell.has_wall(constants.SOUTH)
                ):
                    edges += 1

        return edges - vertices + 1

    def validate_non_perfect(self) -> bool:
        tolerated_dead_ends: int = self.count_tolerated_dead_ends()
        if not self.braid_maze():
            return False

        return (
            len(self.find_dead_ends()) <= tolerated_dead_ends
            and not self._has_open_3x3()
            and self.count_loops() >= 2
        )

    def generate(self) -> None:
        max_attempts = 20

        for _ in range(max_attempts):
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
            if self._is_perfect:
                return
            if self.validate_non_perfect():
                return

        raise MazeGenerationError("Could not create a maze without dead ends")

    def output_mazefile(self) -> None:
        file_name: str = self._output_file
        try:
            with open(file_name, "w") as file:
                for row in self.grid:
                    for cell in row:
                        file.write(format(cell.walls, "X"))
                    file.write("\n")
                file.write("\n")
                file.write(f"{self._entry[0]},{self._entry[1]}\n")
                file.write(f"{self._exit[0]},{self._exit[1]}\n")
                path: list[tuple[int, int]] = bfs(
                    self.grid, self._entry, self._exit)
                file.write(path_to_direction(path))
        except PermissionError as error:
            raise MazeGenerationError(
                "Permission denied: "
                f"{file_name}"
                ) from error
        except OSError as error:
            raise MazeGenerationError(
                "Cannot write maze file: "
                f"{file_name}"
                ) from error
