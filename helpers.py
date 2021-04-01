from __future__ import annotations
import globals
from typing import Any
import math

class Vector:
    def __init__(self, x: float, y: int) -> None:
        self.x = x
        self.y = y

    def __add__(self, other: Any) -> Vector:
        if isinstance(other, (int, float)):
            return Vector(self.x + other, self.y + other)
        elif isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y)
        elif isinstance(other, tuple):
            return Vector(self.x + other[0], self.y + other[1])
        else:
            raise TypeError
    __radd__ = __add__

    def __sub__(self, other: Any) -> Vector:
        if isinstance(other, (int, float)):
            return Vector(self.x - other, self.y - other)
        elif isinstance(other, Vector):
            return Vector(self.x - other.x, self.y - other.y)
        elif isinstance(other, tuple):
            return Vector(self.x - other[0], self.y - other[1])
        else:
            raise TypeError

    def __mul__(self, other: Any) -> Vector:
        if isinstance(other, (int, float)):
            return Vector(self.x * other, self.y * other)
        elif isinstance(other, Vector):
            return Vector(self.x * other.x, self.y * other.y)
        elif isinstance(other, tuple):
            return Vector(self.x * other[0], self.y * other[1])
        else:
            raise TypeError
    __rmul__ = __mul__

    def __truediv__(self, other: Any) -> Vector:
        if isinstance(other, (int, float)):
            return Vector(self.x / other, self.y / other)
        elif isinstance(other, Vector):
            return Vector(self.x / other.x, self.y / other.y)
        elif isinstance(other, tuple):
            return Vector(self.x / other[0], self.y / other[1])
        else:
            raise TypeError

    def __neg__(self) -> Vector:
        return Vector(-self.x, -self.y)

    def __round__(self, n: int = None):
        return Vector(round(self.x, n), round(self.y, n))

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Vector):
            return math.isclose(self.x, other.x) and math.isclose(self.y, other.y)
        elif isinstance(other, tuple):
            return math.isclose(self.x, other[0]) and math.isclose(self.y, other[1])
        else:
            return False

    def __getitem__(self, item: int) -> float:
        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        else:
            raise IndexError

    def __copy__(self) -> Vector:
        return Vector(self.x, self.y)

    def __repr__(self):
        return f'Vector({self.x}, {self.y})'

    def set(self, other: Vector) -> None:
        self.x = other.x
        self.y = other.y

    def tuple(self) -> tuple[float, float]:
        return self.x, self.y

    def int_tuple(self) -> tuple[float, float]:
        return round(self.x), round(self.y)

    def lerp(self, target: Vector, magnitude: float):
        self.x = lerp(self.x, target.x, magnitude)
        self.y = lerp(self.y, target.y, magnitude)


def grid_distance(position: Vector, target: Vector) -> int:
    distances = position - target
    return abs(distances.x) + abs(distances.y)

def lerp(position: float, target: float, magnitude: float) -> float:
    if position > target:
        return max(position - abs(magnitude), target)
    elif position < target:
        return min(position + abs(magnitude), target)
    else:
        return target

def within_grid(vector: Vector) -> bool:
    return 0 <= vector.x < globals.GRID_SIZE.x and 0 <= vector.y < globals.GRID_SIZE.y
