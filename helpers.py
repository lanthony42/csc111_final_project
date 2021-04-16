from vector import Vector
import game_constants as const


def grid_distance(position: Vector, target: Vector) -> int:
    distances = position - target
    return abs(distances.x) + abs(distances.y)


def within_grid(vector: Vector) -> bool:
    return 0 <= vector.x < const.GRID_SIZE.x and 0 <= vector.y < const.GRID_SIZE.y


def clamp(number: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(max_val, number))


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['game_constants', 'vector'],
        'max-line-length': 100,
        'disable': ['E1136']
    })

    import python_ta.contracts
    python_ta.contracts.DEBUG_CONTRACTS = True
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()
