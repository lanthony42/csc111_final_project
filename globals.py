from helpers import Vector
import pygame


TILE_SIZE = Vector(16, 16)
TILE_CENTER_X = Vector(TILE_SIZE.x / 2, 0)
GRID_SIZE = Vector(28, 36)
SCREEN_SIZE = TILE_SIZE * GRID_SIZE

DEFAULT_POS = Vector(14, 14) * TILE_SIZE - TILE_CENTER_X
PLAYER_POS = Vector(14, 26) * TILE_SIZE - TILE_CENTER_X
GHOST_POS = (DEFAULT_POS,
             Vector(14, 17) * TILE_SIZE - TILE_CENTER_X,
             Vector(12, 17) * TILE_SIZE - TILE_CENTER_X,
             Vector(16, 17) * TILE_SIZE - TILE_CENTER_X)

DIRECTION_ORDER = (pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN, pygame.K_RIGHT)
DIRECTION = {pygame.K_UP: Vector(0, -1),
             pygame.K_LEFT: Vector(-1, 0),
             pygame.K_DOWN: Vector(0, 1),
             pygame.K_RIGHT: Vector(1, 0)}
CORNER = {(0, -1): (-TILE_SIZE.y / 8, TILE_SIZE.y * 3/ 8),
          (-1, 0): (-TILE_SIZE.x / 8, TILE_SIZE.x * 3 / 8),
          (0, 1): (-TILE_SIZE.y * 3 / 8, TILE_SIZE.y / 8),
          (1, 0): (-TILE_SIZE.x * 3 / 8, TILE_SIZE.x / 8)}
DEFAULT_DIR = Vector(0, 0)
PLAYER_DIR = DIRECTION[pygame.K_LEFT]
DEFAULT_SPEED = 4.0
PLAYER_SPEED = 4.5

# Colours
YELLOW = (253, 255, 0)
RED = (208, 62, 25)
PINK = (234, 130, 229)
TEAL = (70, 191, 238)
ORANGE = (219, 133, 28)
GHOST_COLOURS = (RED, PINK, TEAL, ORANGE)

# Tile Types
EMPTY = '0'
WALL = '1'
DOT = '2'
BOOST = '5'
DOOR = '8'
OUT = '9'
BAD_TILES = {WALL, DOOR, OUT}

DOT_SCORE = 10
BOOST_SCORE = 50
DEFAULT_LIVES = 3
FPS = 24

# Round Timings
ROUND_START = 2 * FPS
ROUND_PATTERN = ((7 * FPS, 'scatter'), (20 * FPS, 'chase'),
                 (7 * FPS, 'scatter'), (20 * FPS, 'chase'),
                 (5 * FPS, 'scatter'), (20 * FPS, 'chase'),
                 (5 * FPS, 'scatter'), (None, 'chase'))
