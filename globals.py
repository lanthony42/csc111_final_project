from helpers import Vector
import pygame


TILE_SIZE = Vector(16, 16)
GRID_SIZE = Vector(28, 36)
SCREEN_SIZE = TILE_SIZE * GRID_SIZE

DEFAULT_POS = Vector(14, 26) * TILE_SIZE - (TILE_SIZE.x / 2, 0)
DIRECTION_ORDER = [pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN, pygame.K_RIGHT]
DIRECTION = {pygame.K_UP: Vector(0, -1),
             pygame.K_LEFT: Vector(-1, 0),
             pygame.K_DOWN: Vector(0, 1),
             pygame.K_RIGHT: Vector(1, 0)}
CORNER = {(0, -1): (-TILE_SIZE.y / 8, TILE_SIZE.y * 3/ 8),
          (-1, 0): (-TILE_SIZE.x / 8, TILE_SIZE.x * 3 / 8),
          (0, 1): (-TILE_SIZE.y * 3 / 8, TILE_SIZE.y / 8),
          (1, 0): (-TILE_SIZE.x * 3 / 8, TILE_SIZE.x / 8)}
DEFAULT_SPEED = 2.0

# Colours
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
PINK = (255, 100, 100)
TEAL = (100, 100, 255)
ORANGE = (255, 200, 0)
GHOST_COLOURS = [RED, PINK, TEAL, ORANGE]

# Tile Types
EMPTY = '0'
WALL = '1'
DOT = '2'
BOOST = '5'
OUT = '9'

DOT_SCORE = 10
BOOST_SCORE = 50
FPS = 24
