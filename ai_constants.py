import game_constants as g_const


DIRECTION_ROTATE = tuple(g_const.DIRECTION[direction] for direction in g_const.DIRECTION_ORDER * 2)
POINT_TIMEOUT = 15 * g_const.FPS
POINT_OFFSET = 125 * g_const.FPS

# Neural Network Constants
ACTIVE = 1.0
INACTIVE = 0.0
DOTS_BIAS = 8
THRESHOLD = 0.65

INPUT_SIZE = 14
OUTPUT_SIZE = 3
HIDDEN_SIZE = 5

# Training Constants
WIN_WEIGHT = 1000.0
SCORE_WEIGHT = 1.0
TIME_WEIGHT = 0.25

TRAVERSAL_STAGE = 0
GHOST_STAGE = 1
BOOST_STAGE = 2

SCORE_THRESHOLD = (2400, 1800, 2600)

# Mutation Constants
RANDOM_CHANCE = 0.05
EXPANSION_CHANCE = 0.5
EXPLORATION_CO = 5.0

WEIGHT_CO = 40
FITNESS_CO = 100
WEIGHT_OFFSET = SCORE_WEIGHT * (WEIGHT_CO - 1)


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
