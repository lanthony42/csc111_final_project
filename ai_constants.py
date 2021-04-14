import game_constants as g_const


DIRECTION_ROTATE = tuple(g_const.DIRECTION[direction] for direction in g_const.DIRECTION_ORDER * 2)
POINT_TIMEOUT = 15 * g_const.FPS

ACTIVE = 1.0
INACTIVE = 0.0


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['game_constants'],
        'max-line-length': 100,
        'disable': ['E1136']
    })

    import python_ta.contracts
    python_ta.contracts.DEBUG_CONTRACTS = True
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()
