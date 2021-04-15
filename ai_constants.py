import game_constants as g_const


DIRECTION_ROTATE = tuple(g_const.DIRECTION[direction] for direction in g_const.DIRECTION_ORDER * 2)
POINT_TIMEOUT = 15 * g_const.FPS

# Neural Network Constants
ACTIVE = 1.0
INACTIVE = 0.0
DOTS_BIAS = 8
THRESHOLD = 0.8

INPUT_SIZE = 14
OUTPUT_SIZE = 4

# Training Constants
WIN_WEIGHT = 4000.0
SCORE_WEIGHT = 1.0
TIME_WEIGHT = 0.1

TRAVERSAL_STAGE = 1
GHOST_STAGE = 2
BOOST_STAGE = 3


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
