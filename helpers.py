"""CSC111 Final Project

Module containing useful helper functions, to be used in other modules.
"""
from vector import Vector
import game_constants as const


def grid_distance(position: Vector, target: Vector) -> float:
    """Returns the the grid distance from the position to target vectors.

    Args:
        - position: The first vector to check.
        - target: The second vector to check.

    >>> grid_distance(Vector(0, 0), Vector(1, 1))
    2
    >>> grid_distance(Vector(2, 2), Vector(2, 2))
    0
    """
    distances = position - target
    return abs(distances.x) + abs(distances.y)


def within_grid(vector: Vector) -> bool:
    """Returns whether or not vector is within the grid bounds.

    Args:
        - position: The vector to check position of.

    >>> within_grid(Vector(0, 0))
    True
    """
    return 0 <= vector.x < const.GRID_SIZE.x and 0 <= vector.y < const.GRID_SIZE.y


def clamp(number: float, min_val: float, max_val: float) -> float:
    """Retuned the value of number clamped between min_val and max_val.

    Args:
        - number: The number to be clamped.
        - min_val: The minimum value of the returned number.
        - max_val: The maximum value of the returned number.

    Preconditions:
        - min_val <= max_val

    >>> clamp(0.0, 1.0, 2.0)
    1.0
    >>> clamp(5.0, 1.0, 2.0)
    2.0
    >>> clamp(1.5, 1.0, 2.0)
    1.5
    """
    return max(min_val, min(max_val, number))


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['game_constants', 'vector'],
        'max-line-length': 100,
        'disable': ['E1136']
    })

    import python_ta.contracts
    python_ta.contracts.DEBUG_CONTRACTS = False
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()
