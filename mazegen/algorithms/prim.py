from amazing import MazeGenerationError
from cell import Cell
from utils import remove_wall, is_inside
import constants
import random

def get_frontiers(
    grid: list[list[Cell]],
    visited: set[tuple[int, int]],
    cur_cell: Cell,
    frontiers: list[tuple[int, int, int, int, int]]
    ) -> None:
    x: int = cur_cell.x
    y: int = cur_cell.y
    width = len(grid[0])
    height = len(grid)
    for direction, (dx, dy) in constants.DIRECTIONS.items():
        nx = x + dx
        ny = y + dy
        if not is_inside(nx, ny, width, height):
            continue
        if (nx, ny) in visited:
            continue
        if grid[ny][nx].blocked:
            continue
        if not cur_cell.has_wall(direction):
            continue
        frontiers.append((x, y, nx, ny, direction))

def prim(grid: list[list[Cell]], rng: random.Random) -> None:
    accessible_count: int = sum(
        1
        for row in grid
        for cell in row
        if not cell.blocked
    )

    available_cells: list[Cell] = [
        cell
        for row in grid
        for cell in row
        if not cell.blocked
    ]
    start = rng.choice(available_cells)

    visited: set[tuple[int, int]] = {(start.x, start.y)}
    frontiers: list[tuple[int, int, int, int, int]] = []
    get_frontiers(
        grid, visited, start, frontiers
        )
    while frontiers:
        index = rng.randrange(len(frontiers))

        x, y, nx, ny, direction = frontiers.pop(index)
        if (nx, ny) in visited:
            continue
        remove_wall(grid[y][x], grid[ny][nx], direction)
        visited.add((nx, ny))
        get_frontiers(
            grid, visited, grid[ny][nx], frontiers,
        )
    if len(visited) != accessible_count:
        raise MazeGenerationError("Not all accessible cells could be reached")
