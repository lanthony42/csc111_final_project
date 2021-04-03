from __future__ import annotations

from typing import Any
import math


class Vector:
    x: float
    y: float

    def __init__(self, x: float, y: float) -> None:
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

    def __radd__(self, other: Any) -> Vector:
        return self.__add__(other)

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

    def __rmul__(self, other: Any) -> Vector:
        return self.__mul__(other)

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

    def __round__(self, n: int = None) -> Vector:
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

    def __repr__(self) -> str:
        return f'Vector({self.x}, {self.y})'

    def set(self, other: Vector) -> None:
        self.x = other.x
        self.y = other.y

    def tuple(self) -> tuple[float, float]:
        return self.x, self.y

    def int_tuple(self) -> tuple[float, float]:
        return round(self.x), round(self.y)

    def lerp(self, target: Vector, magnitude: float) -> None:
        self.x = lerp(self.x, target.x, magnitude)
        self.y = lerp(self.y, target.y, magnitude)


def lerp(position: float, target: float, magnitude: float) -> float:
    if position > target:
        return max(position - abs(magnitude), target)
    elif position < target:
        return min(position + abs(magnitude), target)
    else:
        return target


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['math'],
        'max-line-length': 100,
        'disable': ['E1136']
    })

    import python_ta.contracts
    python_ta.contracts.DEBUG_CONTRACTS = True
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()
