import pygame
from vector import Vector


# Game Size Constants
TILE_SIZE = Vector(16, 16)
TILE_CENTER_X = Vector(TILE_SIZE.x / 2, 0)
GRID_SIZE = Vector(28, 36)
SCREEN_SIZE = TILE_SIZE * GRID_SIZE

# Gameplay Constants
DOT_SCORE = 10
BOOST_SCORE = 50
GHOST_SCORE = (50, 100, 200, 400)
DEFAULT_LIVES = 3
FPS = 24

# Positioning Constants
DEFAULT_POS = Vector(14, 14) * TILE_SIZE - TILE_CENTER_X
PLAYER_POS = Vector(14, 26) * TILE_SIZE - TILE_CENTER_X
HOME_POS = Vector(14, 17) * TILE_SIZE - TILE_CENTER_X
GHOST_POS = (DEFAULT_POS, HOME_POS,
             Vector(12, 17) * TILE_SIZE - TILE_CENTER_X,
             Vector(16, 17) * TILE_SIZE - TILE_CENTER_X)

# Movement Constants
DIRECTION_ORDER = (pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN, pygame.K_RIGHT)
DIRECTION = {pygame.K_UP: Vector(0, -1),
             pygame.K_LEFT: Vector(-1, 0),
             pygame.K_DOWN: Vector(0, 1),
             pygame.K_RIGHT: Vector(1, 0)}
CORNER = {(0, -1): (-TILE_SIZE.y / 8, TILE_SIZE.y * 3 / 8),
          (-1, 0): (-TILE_SIZE.x / 8, TILE_SIZE.x * 3 / 8),
          (0, 1): (-TILE_SIZE.y * 3 / 8, TILE_SIZE.y / 8),
          (1, 0): (-TILE_SIZE.x * 3 / 8, TILE_SIZE.x / 8)}

DEFAULT_DIR = Vector(0, 0)
PLAYER_DIR = DIRECTION[pygame.K_LEFT]
BASE_SPEED = 10 * TILE_SIZE.x / FPS
DEFAULT_SPEED = round(BASE_SPEED * 0.75, 2)
PLAYER_SPEED = round(BASE_SPEED * 0.8, 2)

# Colours
YELLOW = (253, 255, 0)
RED = (208, 62, 25)
PINK = (234, 130, 229)
TEAL = (70, 191, 238)
ORANGE = (219, 133, 28)
FRIGHT = (100, 100, 200)
GHOST_COLOURS = (RED, PINK, TEAL, ORANGE)

# Tile Types
EMPTY = '0'
WALL = '1'
DOT = '2'
BOOST = '5'
DOOR = '8'
OUT = '9'
BAD_TILES = {WALL, DOOR, OUT}

# Round Timings
BOOST_TIME = 6 * FPS
GHOST_RELEASE = 5.5 * FPS
ROUND_START = 2 * FPS
ROUND_PATTERN = ((7 * FPS, 'scatter'), (20 * FPS, 'chase'),
                 (7 * FPS, 'scatter'), (20 * FPS, 'chase'),
                 (5 * FPS, 'scatter'), (20 * FPS, 'chase'),
                 (5 * FPS, 'scatter'), (None, 'chase'))
HOME_TIME = 2 * FPS


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['pygame', 'vector'],
        'max-line-length': 100,
        'disable': ['E1136', 'E1101']
    })

    import python_ta.contracts
    python_ta.contracts.DEBUG_CONTRACTS = True
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()
