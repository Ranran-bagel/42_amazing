# constants.py
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