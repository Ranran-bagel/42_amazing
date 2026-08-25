from dataclasses import dataclass
from amazing import MazeGenerationError, PatternError
from collections import deque
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

FORTY_TWO_WIDTH = 7
FORTY_TWO_HEIGHT = 5

FORTY_TWO_PATTERN = (
    (0, 0),                 (4, 0), (5, 0), (6, 0),

    (0, 1),                                 (6, 1),

    (0, 2), (1, 2), (2, 2), (4, 2), (5, 2), (6, 2),

                    (2, 3), (4, 3),

                    (2, 4), (4, 4), (5, 4), (6, 4),
)

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

    def close_wall(self, direction: int) -> None:
        self.walls |= direction

class MazeGenerator:
    def __init__(
        self, entry: tuple[int, int], exit: tuple[int, int],
        width: int, height: int, seed: int, perfect: bool
        ) -> None:
        self._entry = entry
        self._exit = exit
        self._width: int = width
        self._height: int = height
        self.stack: list[tuple[int, int]] = list()
        self._is_perfect = perfect
        self._seed = seed
        self.rng = random.Random(self._seed)
        self.grid = [
            [Cell(x, y) for x in range(self._width)]
            for y in range(self._height)
        ]

    def reset_grid(self) -> None:
        self.grid = [
                    [Cell(x, y) for x in range(self._width)]
                    for y in range(self._height)
                ]

    def is_inside(self, x: int, y: int) -> bool:
        return (
            0 <= x < self._width and 0 <= y < self._height
            )

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

    def get_unvisited_neighbors(self, cur_cell: Cell, visited: list[tuple[int, int]]) -> list[tuple[int, int, int]]:
        neighbors: list[tuple[int, int, int]] = []
        x: int = cur_cell.x
        y: int = cur_cell.y
        for direction, (dx, dy) in DIRECTIONS.items():
            nx = x + dx
            ny = y + dy

            if not self.is_inside(nx, ny):
                continue
            if (nx, ny) in visited:
                continue
            if self.grid[ny][nx].blocked:
                continue
            neighbors.append((direction, nx, ny))
        return neighbors

    def remove_wall(self, cur_cell: Cell, next_cell: Cell, direction: int) -> None:
        cur_cell.open_wall(direction)
        next_cell.open_wall(OPPOSITE[direction])

    def add_wall(self, cur_cell: Cell, next_cell: Cell, direction: int) -> None:
        cur_cell.close_wall(direction)
        next_cell.close_wall(OPPOSITE[direction])

    def _is_open_3x3(self, start_x: int, start_y: int) -> bool:
        for y in range(start_y, start_y + 3):
            for x in range(start_x, start_x + 2):
                if self.grid[y][x].has_wall(EAST):
                    return False

        for y in range(start_y, start_y + 2):
            for x in range(start_x, start_x + 3):
                if self.grid[y][x].has_wall(SOUTH):
                    return False

        return True

    def _has_open_3x3(self) -> bool:
        for y in range(self._height - 2):
            for x in range(self._width - 2):
                if self._is_open_3x3(x, y):
                    return True
        return False

    def _add_loops(self) -> None:
        candidates: list[tuple[int, int, int]] = []
        loops_added: int = 0
        for row in self.grid:
            for cell in row:
                x, y = cell.x, cell.y
                if self.is_inside(x + 1, y):
                    east_cell = self.grid[y][x + 1]
                else:
                    east_cell = None
                if self.is_inside(x, y + 1):
                    south_cell = self.grid[y + 1][x]
                else:
                    south_cell = None
                if cell.blocked:
                    continue
                if east_cell and not east_cell.blocked and cell.has_wall(EAST):
                    candidates.append((cell, east_cell, EAST))
                if south_cell and not south_cell.blocked and cell.has_wall(SOUTH):
                    candidates.append((cell, south_cell, SOUTH))
                else:
                    continue
        target: int = max(1, len(candidates) // 10)
        self.rng.shuffle(candidates)
        for cell, next_cell, direction in candidates:
            if loops_added >= target:
                break
            self.remove_wall(cell, next_cell, direction)
            if self._has_open_3x3():
                self.add_wall(cell, next_cell, direction)
                continue
            loops_added += 1

    def dfs(self) -> None:
        accessible_count = sum(
            1
            for row in self.grid
            for cell in row
            if not cell.blocked
        )

        available_cells = [
            cell
            for row in self.grid
            for cell in row
            if not cell.blocked
        ]
        start = self.rng.choice(available_cells)

        visited: set[tuple[int, int]] = set()
        visited = {(start.x, start.y)}
        self.stack = [(start.x, start.y)]
    
        while self.stack:
            x, y = self.stack[-1]
            cur_cell = self.grid[y][x]
            neighbors = self.get_unvisited_neighbors(cur_cell, visited)

            if neighbors:
                direction, nx, ny = self.rng.choice(neighbors)
                next_cell = self.grid[ny][nx]

                self.remove_wall(cur_cell, next_cell, direction)
                visited.add((next_cell.x, next_cell.y))
                self.stack.append((next_cell.x, next_cell.y))

            else:
                self.stack.pop()
        if len(visited) != accessible_count:
            raise MazeGenerationError("Not all accessible cells could be reached")

    def generate(self) -> None:
        self.reset_grid()
        try:
            self._create_42()
        except PatternError as error:
            print(f"ERROR: {error}")
        try:
            self.dfs()
        except MazeGenerationError as error:
            print(f"ERROR: {error}")
        if not self._is_perfect:
            self._add_loops()

    def bfs(self) -> list[tuple[int, int]]:
        queue = deque([self._entry])
        visited: set[tuple[int, int]] = set((self._entry))
        parent: dict = {}
        while queue:
            current = queue.popleft()
            if current == exit:
                break

            x, y = current
            cell = self.grid[y][x]
            for direction in DIRECTIONS:
                (dx, dy) = DIRECTIONS[direction]
                if cell.has_wall(direction):
                    continue
                neighbor = (x + dx, y + dy)
                if neighbor in visited:
                    continue
                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)
        path: list = []
        node = self._exit
        while node != self._entry:
            path.append(node)
            node = parent[node]
        path.append(self._entry)
        path.reverse()
        return path

    def path_to_direction(self, path: list) -> str:
        directions: list = []
        for (x1, y1), (x2, y2) in zip(path, path[1:]):
            dx, dy = x2 - x1, y2 - y1
            if dy == -1:
                directions.append("N")
            elif dy == 1:
                directions.append("S")
            elif dx == 1:
                directions.append("E")
            elif dx == -1:
                directions.append("W")
        return "".join(directions)

    def output_mazefile(self, file_name: str) -> None:
        try:
            with open(file_name, "w") as file:
                for row in self.grid:
                    for cell in row:
                        file.write(format(cell.walls, "X"))
                    file.write("\n")
                file.write("\n")
                file.write(f"{self._entry[0]}, {self._entry[1]}\n")
                file.write(f"{self._exit[0]}, {self._exit[1]}\n")
                path:list[tuple[int, int]] = self.bfs()
                file.write(self.path_to_direction(path))
        except PermissionError as error:
            raise MazeGenerationError(f"Permission denied: {file_name}") from error
        except OSError as error:
            raise MazeGenerationError(f"Cannot write maze file: {file_name}") from error
