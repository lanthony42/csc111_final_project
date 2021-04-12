from __future__ import annotations

from copy import copy
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING
import pygame

from helpers import within_grid
from vector import Vector
import constants as const

# Only imports when type-checking to avoid circular import issues
if TYPE_CHECKING:
    import controls


@dataclass
class ActorState:
    position: Vector
    direction: Vector
    colour: tuple[int, int, int]
    speed: float


class Actor:
    _default_state: ActorState
    state: ActorState
    _queued_direction: Optional[Vector]
    cornering: bool

    def __init__(self, default_state: ActorState = ActorState(const.PLAYER_POS, const.PLAYER_DIR,
                                                              const.YELLOW, const.PLAYER_SPEED),
                 cornering: bool = True) -> None:
        self._default_state = default_state
        self.state = ActorState(copy(default_state.position), default_state.direction,
                                default_state.colour, default_state.speed)

        self._queued_direction = None
        self.cornering = cornering

    def tile(self) -> Vector:
        return round(self.state.position / const.TILE_SIZE)

    def rect(self) -> pygame.Rect:
        return pygame.Rect(*self.state.position, *const.TILE_SIZE)

    def change_direction(self, grid: list[list[int]], direction: Vector) -> None:
        if direction in const.DIRECTION.values():
            tile = self.tile()
            next_tile = tile + direction

            if self.cornering:
                cornering = const.CORNER.get(self.state.direction.int_tuple())
            else:
                cornering = (-self.state.speed / 2, self.state.speed / 2)

            if self.state.direction.y != 0:
                target = tile.y * const.TILE_SIZE.y
                within_cornering = (target + cornering[0] < self.state.position.y
                                    < target + cornering[1])
            elif self.state.direction.x != 0:
                target = tile.x * const.TILE_SIZE.x
                within_cornering = (target + cornering[0] < self.state.position.x
                                    < target + cornering[1])
            else:
                within_cornering = True
            same_axis = abs(self.state.direction.x) == abs(direction.x)

            if within_grid(next_tile) and (within_cornering or same_axis) and \
                    grid[next_tile.y][next_tile.x] not in const.BAD_TILES:
                self.state.direction = direction
                self._queued_direction = None
            else:
                self._queued_direction = direction

    def update(self, grid: list[list[int]]) -> None:
        if self._queued_direction is not None:
            self.change_direction(grid, self._queued_direction)

        tile = self.tile()
        next_tile = self.tile() + self.state.direction

        if not within_grid(next_tile) or grid[next_tile.y][next_tile.x] in const.BAD_TILES:
            next_tile = tile

        if self.state.direction.y != 0:
            target = Vector(tile.x, next_tile.y) * const.TILE_SIZE
        elif self.state.direction.x != 0:
            target = Vector(next_tile.x, tile.y) * const.TILE_SIZE
        else:
            target = self.state.position

        self.state.position.lerp(target, self.state.speed)

    def reset(self, position: Optional[Vector] = None) -> None:
        if position is None:
            self.reset_position()
        else:
            self.state.position = copy(position)

        self.reset_direction()
        self.reset_colour()
        self.reset_speed()

    def reset_position(self) -> None:
        self.state.position = copy(self._default_state.position)

    def reset_direction(self) -> None:
        self.state.direction = self._default_state.direction
        self._queued_direction = None

    def reset_colour(self) -> None:
        self.state.colour = self._default_state.colour

    def reset_speed(self) -> None:
        self.state.speed = self._default_state.speed

    def draw(self, screen: pygame.Surface, debug: bool = False) -> None:
        if debug:
            tile_position = self.tile() * const.TILE_SIZE
            pygame.draw.rect(screen, (100, 100, 0), pygame.Rect(*tile_position, *const.TILE_SIZE))

            next_position = (self.tile() + self.state.direction) * const.TILE_SIZE
            pygame.draw.rect(screen, (100, 0, 0), pygame.Rect(*next_position, *const.TILE_SIZE))

            start_position = self.state.position + 8
            end_direction = start_position + self.state.direction * 20
            pygame.draw.line(screen, (200, 200, 0), start_position.tuple(),
                             end_direction.tuple(), 4)

            if self._queued_direction is not None:
                end_queue_dir = start_position + self._queued_direction * 20
                pygame.draw.line(screen, (200, 50, 0), start_position.tuple(),
                                 end_queue_dir.tuple(), 4)

        pygame.draw.rect(screen, self.state.colour, self.rect())


class TimerState:
    mode_level: int
    round_timer: int
    start_timer: int
    release_level: int
    release_timer: int
    boost_level: int
    boost_timer: int

    def __init__(self) -> None:
        # Round timers
        self.mode_level = 0
        self.round_timer = const.ROUND_PATTERN[self.mode_level][0]
        self.start_timer = const.ROUND_START

        # Ghost release timer
        self.release_level = 0
        self.release_timer = 0

        # Boost timer
        self.boost_level = 0
        self.boost_timer = 0

    def update(self) -> None:
        if self.release_timer >= const.GHOST_RELEASE:
            self.release_timer = 0
            self.release_level += 1
        elif self.release_level < 3:
            self.release_timer += 1

        if self.boost_timer > 0:
            self.boost_timer -= 1

        # Update round pattern
        if self.round_timer is not None:
            if self.round_timer <= 0:
                self.mode_level += 1
                self.round_timer = const.ROUND_PATTERN[self.mode_level][0]
            else:
                self.round_timer -= 1

    def set_start(self) -> None:
        self.start_timer = const.ROUND_START

    def check_start(self) -> bool:
        if pygame.display.get_init() and self.start_timer > 0:
            self.start_timer -= 1
            return True
        else:
            return False

    def set_release(self) -> None:
        self.release_timer = 0
        self.release_level = 0

    def set_boost(self) -> None:
        self.boost_timer = const.BOOST_TIME
        self.boost_level = 0

    def check_boost(self) -> bool:
        return self.boost_timer <= 0


class GameState:
    # Player is last element in self.controllers
    controllers: list[controls.Controller]
    events: Optional[list[pygame.event.Event]]
    lost_life: bool
    lives: int
    score: int
    dot_counter: int
    timers: TimerState

    def __init__(self, lives: int) -> None:
        self.controllers = []
        self.events = None

        self.lost_life = False
        self.lives = lives
        self.score = 0

        self.dot_counter = 0
        self.timers = TimerState()

    def player(self) -> controls.Controller:
        return self.controllers[-1]

    def player_actor(self) -> Actor:
        return self.controllers[-1].actor

    def ghosts(self) -> list[controls.Controller]:
        return self.controllers[:-1]

    def ghosts_actor(self) -> list[Actor]:
        return [control.actor for control in self.controllers[:-1]]

    def mode(self) -> str:
        return const.ROUND_PATTERN[self.timers.mode_level][1]


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['copy', 'dataclasses', 'pygame', 'constants', 'controls', 'helpers',
                          'vector'],
        'max-line-length': 100,
        'disable': ['E1136']
    })

    import python_ta.contracts
    python_ta.contracts.DEBUG_CONTRACTS = True
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()
