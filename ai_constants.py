"""CSC111 Final Project

Module with constants relevant to AI, to be used in other modules.
"""
import game_constants as g_const


# Neural Network Input Constants
DIRECTION_ROTATE = tuple(g_const.DIRECTION[direction] for direction in g_const.DIRECTION_ORDER * 2)
POINT_TIMEOUT = 15 * g_const.FPS
POINT_OFFSET = 125 * g_const.FPS

# General Neural Network Constants
ACTIVE = 1.0
INACTIVE = 0.0
DOTS_BIAS = 8
MOVE_THRESHOLD = 0.65

INPUT_SIZE = 14
OUTPUT_SIZE = 3
HIDDEN_SIZE = 5

# Training Constants
WIN_WEIGHT = 1000.0
SCORE_WEIGHT = 1.0
TIME_WEIGHT = 0.4

TRAVERSAL_STAGE = 0
GHOST_STAGE = 1
BOOST_STAGE = 2

SCORE_THRESHOLD = (2400, 1500, 2400)
STALENESS_THRESHOLD = 50
EXTINCTION_MIN = 15
EXTINCTION_AMOUNT = 5

ROLLING_AVG_COUNT = 100
SIMULATION_SEED = 45

# Mutation Constants
RANDOM_CHANCE = 0.05
EXPANSION_CHANCE = 0.5
EXPLORATION_CO = 4.7

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
    python_ta.contracts.DEBUG_CONTRACTS = False
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()
