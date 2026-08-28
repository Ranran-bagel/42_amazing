from amazing import MazeGenerationError
from cell import Cell
from utils import remove_wall, is_inside
import constants
import random

def get_unvisited_neighbors(
    grid: list[list[Cell]], 
    cur_cell: Cell,
    visited: list[tuple[int, int]],
    width: int,
    height: int,
    ) -> list[tuple[int, int, int]]:
    neighbors: list[tuple[int, int, int]] = []
    x: int = cur_cell.x
    y: int = cur_cell.y
    for direction, (dx, dy) in constants.DIRECTIONS.items():
        nx = x + dx
        ny = y + dy
        if not is_inside(nx, ny, width, height):
            continue
        if (nx, ny) in visited:
            continue
        if grid[ny][nx].blocked:
            continue
        neighbors.append((direction, nx, ny))
    return neighbors

def dfs(grid: list[list[Cell]], rng: random.Random) -> None:
    accessible_count = sum(
        1
        for row in grid
        for cell in row
        if not cell.blocked
    )

    available_cells = [
        cell
        for row in grid
        for cell in row
        if not cell.blocked
    ]
    start = rng.choice(available_cells)

    visited: set[tuple[int, int]] = {(start.x, start.y)}
    stack: list[tuple[int, int]] = [(start.x, start.y)]
    width = len(grid[0])
    height = len(grid)

    while stack:
        x, y = stack[-1]
        cur_cell = grid[y][x]
        neighbors = get_unvisited_neighbors(grid, cur_cell, visited, width, height)

        if neighbors:
            direction, nx, ny = rng.choice(neighbors)
            next_cell = grid[ny][nx]

            remove_wall(cur_cell, next_cell, direction)
            visited.add((next_cell.x, next_cell.y))
            stack.append((next_cell.x, next_cell.y))

        else:
            stack.pop()
    if len(visited) != accessible_count:
        raise MazeGenerationError("Not all accessible cells could be reached")