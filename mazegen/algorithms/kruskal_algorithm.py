from ..cell import Cell
from .. import constants
from .utils import is_inside, remove_wall
from ..exceptions import MazeGenerationError
import random


def init_parent(
    grid: list[list[Cell]],
) -> dict[tuple[int, int], tuple[int, int]]:
    parent: dict[tuple[int, int], tuple[int, int]] = {}
    for row in grid:
        for cell in row:
            if not cell.blocked:
                position = (cell.x, cell.y)
                parent[position] = position

    return parent


def find(
    parent: dict[tuple[int, int], tuple[int, int]],
    cell: tuple[int, int]
) -> tuple[int, int]:
    if parent[cell] != cell:
        parent[cell] = find(parent, parent[cell])
    if not parent:
        raise MazeGenerationError(
            "No accessible cells available"
        )
    return parent[cell]


def union(
    parent: dict[tuple[int, int], tuple[int, int]],
    current: tuple[int, int],
    neighbor: tuple[int, int],
) -> None:
    root_cur = find(parent, current)
    root_nei = find(parent, neighbor)
    parent[root_cur] = root_nei


def kruskal(grid: list[list[Cell]], rng: random.Random) -> None:
    parent: dict[tuple[int, int], tuple[int, int]] = init_parent(grid)
    width: int = len(grid[0])
    height: int = len(grid)
    edges: list[tuple[int, int, int, int, int]] = []
    for row in grid:
        for cell in row:
            x, y = cell.x, cell.y
            if grid[y][x].blocked:
                continue
            if (is_inside(x + 1, y, width, height)
                    and not grid[y][x + 1].blocked):
                edges.append((x, y, x + 1, y, constants.EAST))
            if (is_inside(x, y + 1, width, height)
                    and not grid[y + 1][x].blocked):
                edges.append((x, y, x, y + 1, constants.SOUTH))
    rng.shuffle(edges)
    for x, y, nx, ny, direction in edges:
        current: tuple[int, int] = (x, y)
        neighbor: tuple[int, int] = (nx, ny)
        if find(parent, current) == find(parent, neighbor):
            continue
        remove_wall(grid[y][x], grid[ny][nx], direction)
        union(parent, current, neighbor)
