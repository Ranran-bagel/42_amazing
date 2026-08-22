from dataclasses import dataclass

@dataclass
class Cell:
    x: int
    y: int
    walls: int = 0b1111
    blocked: bool = True

    def has_wall