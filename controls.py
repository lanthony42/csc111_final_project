from __future__ import annotations
import pygame
from globals import *
from helpers import grid_distance, within_grid
import game


class Controller:
    def __init__(self, game_state: game.Game, actor: game.Actor) -> None:
        self.game_state = game_state
        self.actor = actor

    def control(self) -> None:
        raise NotImplementedError

    def draw_debug(self) -> None:
        raise NotImplementedError


class InputController(Controller):
    def control(self) -> None:
        for event in self.game_state.events:
            if event.type == pygame.KEYDOWN:
                self.actor.change_direction(self.game_state.grid, DIRECTION.get(event.key))

    def draw_debug(self) -> None:
        pass


class GhostController(Controller):
    def __init__(self, game_state: game.Game, actor: game.Actor) -> None:
        super().__init__(game_state, actor)
        self.next_tile = None
        self.next_direction = None

    def control(self) -> None:
        tile = self.actor.tile()
        if self.next_tile is not None and tile != self.next_tile:
            return

        self.actor.change_direction(self.game_state.grid, self.next_direction)
        if self.next_tile is None:
            self.next_tile = tile + self.actor.direction
        else:
            self.next_tile = tile + self.next_direction

        self.next_direction = -self.actor.direction
        best_distance = None
        for key in DIRECTION_ORDER:
            direction = DIRECTION[key]
            candidate = self.next_tile + direction

            if not within_grid(candidate) or candidate == self.actor.tile() or \
                self.game_state.grid[candidate.y][candidate.x] == WALL:
                continue

            distance = grid_distance(candidate, self.target())
            if best_distance is None or distance < best_distance:
                self.next_direction = direction
                best_distance = distance

    def draw_debug(self) -> None:
        next_position = self.next_tile * TILE_SIZE
        pygame.draw.rect(self.game_state.screen, (0, 100, 0),
                         pygame.Rect(*next_position, *TILE_SIZE))

    def target(self) -> Vector:
        return self.game_state.player.tile()
