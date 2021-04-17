"""CSC111 Final Project

Module with containing the Vector class, which stores a vector.
"""
from __future__ import annotations

from typing import Optional, Any
import math


class Vector:
    """A class representing a two dimensional vector.

    Instance Attributes:
        - x: The x-coordinate of the vector.
        - y: the y-coordinate of the vector.
    """
    x: float
    y: float

    def __init__(self, x: float, y: float) -> None:
        """Initialize a vector object.

        Args:
            - x: The x-coordinate of the vector.
            - y: the y-coordinate of the vector.
        """
        self.x = x
        self.y = y

    def __add__(self, other: Any) -> Vector:
        """Adds the vector with another object, returning the resultant vector.

        Args:
            - other: The other object to be added.
        """
        if isinstance(other, (int, float)):
            return Vector(self.x + other, self.y + other)
        elif isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y)
        elif isinstance(other, tuple):
            return Vector(self.x + other[0], self.y + other[1])
        else:
            raise TypeError

    def __radd__(self, other: Any) -> Vector:
        """Adds the object with to this vector, returning the resultant vector.

        Args:
            - other: The object the vector will be added to.
        """
        return self.__add__(other)

    def __sub__(self, other: Any) -> Vector:
        """Subtracts the object from to this vector, returning the resultant vector.

        Args:
            - other: The other object to be subtracted.
        """
        if isinstance(other, (int, float)):
            return Vector(self.x - other, self.y - other)
        elif isinstance(other, Vector):
            return Vector(self.x - other.x, self.y - other.y)
        elif isinstance(other, tuple):
            return Vector(self.x - other[0], self.y - other[1])
        else:
            raise TypeError

    def __mul__(self, other: Any) -> Vector:
        """Multiplies the vector to the other object, returning the resultant vector.

        Args:
            - other: The other object to be multiplied with.
        """
        if isinstance(other, (int, float)):
            return Vector(self.x * other, self.y * other)
        elif isinstance(other, Vector):
            return Vector(self.x * other.x, self.y * other.y)
        elif isinstance(other, tuple):
            return Vector(self.x * other[0], self.y * other[1])
        else:
            raise TypeError

    def __rmul__(self, other: Any) -> Vector:
        """Multiplies the object to this vector, returning the resultant vector.

        Args:
            - other: The other object to be multiplied with.
        """
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
        """Returns a vector with this vector's components having opposite sign."""
        return Vector(-self.x, -self.y)

    def __round__(self, n: Optional[int] = None) -> Vector:
        """Returns a vector with this vector's components rounded.

        Preconditions:
            - n is None or n >= 0

        Args:
            - n: The number of decimals to be rounded to.
        """
        return Vector(round(self.x, n), round(self.y, n))

    def __eq__(self, other: Any) -> bool:
        """Returns whether the other object contains same values, accounting for floating point
        errors.

        Args:
            - other: The object to be compared to.
        """
        if isinstance(other, Vector):
            return math.isclose(self.x, other.x) and math.isclose(self.y, other.y)
        elif isinstance(other, tuple):
            return math.isclose(self.x, other[0]) and math.isclose(self.y, other[1])
        else:
            return False

    def __getitem__(self, item: int) -> float:
        """Returns the vector component given index.

        Preconditions:
            - 0 <= item <= 1

        Args:
            - item: The index of the component to be retrieved.
        """
        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        else:
            raise IndexError

    def __copy__(self) -> Vector:
        """Returns a copy of this vector."""
        return Vector(self.x, self.y)

    def __repr__(self) -> str:
        """Returns text representation of this vector."""
        return f'Vector({self.x}, {self.y})'

    def set(self, other: Vector) -> None:
        """Sets the components of this vector to match that of the other vector's.

        Args:
            - other: The other vector to be set to.
        """
        self.x = other.x
        self.y = other.y

    def tuple(self) -> tuple[float, float]:
        """Returns the vector as a tuple of two floats."""
        return self.x, self.y

    def int_tuple(self) -> tuple[int, int]:
        """Returns the vector as a tuple of two ints."""
        return round(self.x), round(self.y)

    def lerp(self, target: Vector, magnitude: float) -> None:
        """Linearly interpolates this vector towards a target vector, which each component
        changing by a maximum of the magnitude value. Note this function mutations this vector.

        Preconditions:
            - magnitude >= 0

        Args:
            - target: The other vector to be linearly interpolated towards.
            - magnitude: The magnitude of any changes to components.
        """
        self.x = lerp(self.x, target.x, magnitude)
        self.y = lerp(self.y, target.y, magnitude)


def lerp(position: float, target: float, magnitude: float) -> float:
    """Linearly interpolates this position value towards a target value, which changes
    by a maximum of the magnitude value, returning the resulting position.

    Is a helper function for Vector.lerp.

    Preconditions:
        - magnitude >= 0

    Args:
        - position: The value to be linearly interpolated.
        - target: The other value to be linearly interpolated towards.
        - magnitude: The magnitude of any changes to the position value.
    """
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
    python_ta.contracts.DEBUG_CONTRACTS = False
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()
