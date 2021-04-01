"""
TODO:
    - Ghosts
    - Refactor for generalization
"""
import pygame
import controls
from helpers import Vector, within_grid
from globals import *
from copy import copy
from typing import Type
import math
import csv


class Game:
    def __init__(self, map: str) -> None:
        self.clock = pygame.time.Clock()
        self.screen = None
        self.events = None

        self.controls = []
        self.player = None
        self.ghosts = []

        self.game_over = False
        self.lives = 0
        self.score = 0

        # Round variables
        self.mode_ind = 0
        self.round_timer = ROUND_PATTERN[self.mode_ind][0]

        # Load the map
        with open(map) as csv_file:
            reader = csv.reader(csv_file)
            self.grid = list(reader)

    def mode(self) -> str:
        return ROUND_PATTERN[self.mode_ind][1]

    def run(self, player_controller: Type[controls.Controller] = controls.InputController,
            lives: int = DEFAULT_LIVES, visual: bool = True, debug: bool = False) -> int:
        # Reinitialize
        self.player = Actor(position=PLAYER_POS, direction=PLAYER_DIR, speed=PLAYER_SPEED)
        self.ghosts = [Actor(position=position, colour=colour, cornering=False)
                       for position, colour in zip(GHOST_POS, GHOST_COLOURS)]
        self.controls = [controls.InputController(self, self.player),
                         controls.BlinkyController(self, self.ghosts[0]),
                         controls.PinkyController(self, self.ghosts[1]),
                         controls.InkyController(self, self.ghosts[2]),
                         controls.ClydeController(self, self.ghosts[3])]

        self.events = None
        self.game_over = False
        self.lives = lives
        self.score = 0

        # Round variables
        self.mode_ind = 0
        self.round_timer = ROUND_PATTERN[self.mode_ind][0]

        if visual and not pygame.display.get_init():
            self.screen = pygame.display.set_mode(SCREEN_SIZE.tuple())
            pygame.display.set_caption('Pac-Man')
        elif not visual:
            self.screen = None

        while not self.game_over:
            if self.handle_input():
                return self.score

            self.update()

            if visual:
                self.draw(debug)
                self.clock.tick(FPS)

        return (self.check_win(), self.score)

    def handle_input(self) -> bool:
        if not pygame.display.get_init():
            return False

        self.events = pygame.event.get()

        for event in self.events:
            if event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()

                return True
        return False

    def update(self) -> None:
        # Update round pattern
        if self.round_timer is not None:
            if self.round_timer <= 0:
                self.mode_ind += 1
                self.round_timer = ROUND_PATTERN[self.mode_ind][0]
            else:
                self.round_timer -= 1

        # Control actors
        for control in self.controls:
            control.control()

        # Update actors
        self.player.update(self.grid)
        for ghost in self.ghosts:
            ghost.update(self.grid)

            if self.player.rect().colliderect(ghost.rect()):
                pass
                # self.lives -= 1

        # Tile collisions
        tile = self.player.tile()
        if self.grid[tile.y][tile.x] == DOT:
            self.grid[tile.y][tile.x] = EMPTY
            self.score += DOT_SCORE
        elif self.grid[tile.y][tile.x] == BOOST:
            self.grid[tile.y][tile.x] = EMPTY
            self.score += BOOST_SCORE

        # Check win and lose conditions
        if self.check_win() or self.lives <= 0:
            self.game_over = True

    def draw(self, debug: bool = False) -> None:
        self.screen.fill((0, 0, 0))

        if debug:
            for control in self.controls:
                control.draw_debug()

        for y, row in enumerate(self.grid):
            for x, tile in enumerate(row):
                self.draw_tile(tile, x, y, debug)

        for ghost in self.ghosts:
            ghost.draw(self.screen, debug)
        self.player.draw(self.screen, debug)

        pygame.display.update()

    def draw_tile(self, tile: str, x: int, y: int, debug: bool = False) -> None:
        position = TILE_SIZE * (x, y)

        if tile == WALL:
            pygame.draw.rect(self.screen, (0, 0, 255), pygame.Rect(*position, *TILE_SIZE))
        elif tile == DOOR:
            pygame.draw.rect(self.screen, (255, 150, 200), pygame.Rect(*position, *TILE_SIZE))
        elif tile == DOT:
            pygame.draw.circle(self.screen, (200, 200, 150),
                               (position + TILE_SIZE / 2).tuple(), 2)
        elif tile == BOOST:
            pygame.draw.circle(self.screen, (220, 220, 220),
                               (position + TILE_SIZE / 2).tuple(), 5)

        if debug:
            pygame.draw.rect(self.screen, (100, 100, 100),
                             pygame.Rect(*position, *TILE_SIZE),
                             width=1)

    def check_win(self) -> None:
        return not any(tile in {DOT, BOOST} for row in self.grid for tile in row)


class Actor:
    def __init__(self, position: Vector = DEFAULT_POS, direction: Vector = Vector(0, 0),
                 speed: float = DEFAULT_SPEED, colour: tuple[int, int, int] = YELLOW,
                 cornering: bool = True) -> None:
        self.position = copy(position)
        self.direction = direction
        self._home_position = position
        self._queued_direction = None

        self.cornering = cornering
        self.allow_door = False
        self.colour = colour
        self.speed = speed

    def tile(self) -> Vector:
        return round(self.position / TILE_SIZE)

    def rect(self) -> pygame.Rect:
        return pygame.Rect(*self.position, *TILE_SIZE)

    def bad_tiles(self) -> set[str]:
        if self.allow_door:
            return {WALL, OUT}
        else:
            return {WALL, DOOR, OUT}

    def change_direction(self, grid: list[list[int]], direction: Vector) -> None:
        if direction in DIRECTION.values():
            tile = self.tile()
            next_tile = tile + direction

            if self.cornering:
                cornering = CORNER.get(self.direction.int_tuple())
            else:
                cornering = (-self.speed / 2, self.speed / 2)

            if self.direction.y != 0:
                target = tile.y * TILE_SIZE.y
                within_cornering = (target + cornering[0] < self.position.y
                                    < target + cornering[1])
            elif self.direction.x != 0:
                target = tile.x * TILE_SIZE.x
                within_cornering = (target + cornering[0] < self.position.x
                                    < target + cornering[1])
            else:
                within_cornering = True
            same_axis = abs(self.direction.x) == abs(direction.x)

            if within_grid(next_tile) and (within_cornering or same_axis) and \
                    grid[next_tile.y][next_tile.x] not in self.bad_tiles():
                self.direction = direction
                self._queued_direction = None
            else:
                self._queued_direction = direction

    def update(self, grid: list[list[int]]) -> None:
        if self._queued_direction is not None:
            self.change_direction(grid, self._queued_direction)

        tile = self.tile()
        next_tile = self.tile() + self.direction

        if not within_grid(next_tile) or grid[next_tile.y][next_tile.x] in self.bad_tiles():
            next_tile = tile

        if self.direction.y != 0:
            target = Vector(tile.x, next_tile.y) * TILE_SIZE
        elif self.direction.x != 0:
            target = Vector(next_tile.x, tile.y) * TILE_SIZE
        else:
            target = self.position

        self.position.lerp(target, self.speed)

    def draw(self, screen: pygame.Surface, debug: bool = False) -> None:
        if debug:
            tile_position = self.tile() * TILE_SIZE
            pygame.draw.rect(screen, (100, 100, 0), pygame.Rect(*tile_position, *TILE_SIZE))

            next_position = (self.tile() + self.direction) * TILE_SIZE
            pygame.draw.rect(screen, (100, 0, 0), pygame.Rect(*next_position, *TILE_SIZE))

        pygame.draw.rect(screen, self.colour, self.rect())
