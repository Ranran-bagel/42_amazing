from collections import deque
from .cell import Cell
from . import constants

def bfs(
    grid: list[list[Cell]],
    entry: tuple[int, int],
    exit: tuple[int, int]
    ) -> list[tuple[int, int]]:
    queue = deque([entry])
    visited: set[tuple[int, int]] = set((entry))
    parent: dict = {}
    while queue:
        current = queue.popleft()
        if current == exit:
            break

        x, y = current
        cell = grid[y][x]
        for direction in constants.DIRECTIONS:
            (dx, dy) = constants.DIRECTIONS[direction]
            if cell.has_wall(direction):
                continue
            neighbor = (x + dx, y + dy)
            if neighbor in visited:
                continue
            visited.add(neighbor)
            parent[neighbor] = current
            queue.append(neighbor)
    path: list = []
    node = exit
    while node != entry:
        path.append(node)
        node = parent[node]
    path.append(entry)
    path.reverse()
    return path

def path_to_direction(path: list) -> str:
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
