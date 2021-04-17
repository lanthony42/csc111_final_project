"""CSC111 Final Project

Module containing the state classes used to represent states of the game for gameplay.
"""
from __future__ import annotations

from copy import copy
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING
import pygame

from helpers import within_grid
from vector import Vector
import game_constants as const

# Only imports when type-checking to avoid circular import issues
if TYPE_CHECKING:
    import game_controls


@dataclass
class ActorState:
    """A class representing an actor's state.

    Instance Attributes:
        - position: The position of the actor.
        - direction: The direction the actor is facing.
        - colour: The colour of the actor.
        - speed: The speed the actor travels.
    """
    position: Vector
    direction: Vector
    colour: tuple[int, int, int]
    speed: float


class Actor:
    """A class representing an actor.

    Instance Attributes:
        - state: The current state of the actor.
        - cornering: Whether the actor can perform cornering.
    """
    state: ActorState
    cornering: bool

    # Private Instance Attributes:
    #  - _default_state: The original state which the actor can be reset to.
    #  - _queued_direction: The direction queued which can be played when possible.
    _default_state: ActorState
    _queued_direction: Optional[Vector]

    def __init__(self, default_state: ActorState = ActorState(const.PLAYER_POS, const.DEFAULT_DIR,
                                                              const.YELLOW, const.PLAYER_SPEED),
                 cornering: bool = True) -> None:
        """Initializes an actor with the given state.

        Args:
            - default_state: The default and current state for the actor.
            - cornering: Whether the actor will be able to perform cornering.
        """
        self._default_state = default_state
        self.state = ActorState(copy(default_state.position), default_state.direction,
                                default_state.colour, default_state.speed)

        self._queued_direction = None
        self.cornering = cornering

    def tile(self) -> Vector:
        """Return the actor's current tile. """
        return round(self.state.position / const.TILE_SIZE)

    def rect(self) -> pygame.Rect:
        """Return the actor's bounding rectangle. """
        return pygame.Rect(*self.state.position, *const.TILE_SIZE)

    def change_direction(self, grid: list[list[int]], direction: Vector) -> None:
        """Change directions to direction vector depending on if valid at current state.

        Args:
            - grid: The current game's map grid.
            - direction: The direction to be tested if can be changed to.
        """
        if direction in const.DIRECTION.values():
            # Check if valid to turn at current state.
            if (self.within_cornering() or self.same_axis(direction)) and \
                    self.valid_direction(grid, direction):
                self.state.direction = direction
                # Clear direction queue.
                self._queued_direction = None
            else:
                # Queue the direction if not valid yet.
                self._queued_direction = direction

    def valid_direction(self, grid: list[list[int]], direction: Vector) -> bool:
        """Return whether or not direction leads to a valid tile.

        Args:
            - grid: The current game's map grid.
            - direction: The direction to be tested.
        """
        next_tile = self.tile() + direction
        return within_grid(next_tile) and grid[next_tile.y][next_tile.x] not in const.BAD_TILES

    def within_cornering(self) -> bool:
        """Return whether or not player can turn at this point of the tile. """
        tile = self.tile()

        if self.cornering:
            cornering = const.CORNER.get(self.state.direction.int_tuple())
        else:
            cornering = (-self.state.speed / 2, self.state.speed / 2)

        if self.state.direction.y != 0:
            target = tile.y * const.TILE_SIZE.y
            return target + cornering[0] < self.state.position.y < target + cornering[1]
        elif self.state.direction.x != 0:
            target = tile.x * const.TILE_SIZE.x
            return target + cornering[0] < self.state.position.x < target + cornering[1]
        else:
            return True

    def same_axis(self, direction: Vector) -> bool:
        """Return whether or not direction is on same axis as the actor is currently travelling.

        Args:
            - direction: The direction to be tested.
        """
        return abs(self.state.direction.x) == abs(direction.x)

    def update(self, grid: list[list[int]]) -> None:
        """Updates the actor's current state; moves or turns the actor.

        Args:
            - grid: The current game's map grid.
        """
        # Check if can move in queued direction.
        if self._queued_direction is not None:
            self.change_direction(grid, self._queued_direction)

        tile = self.tile()
        next_tile = self.tile() + self.state.direction

        # Gets the next valid tile in direction.
        if not within_grid(next_tile) or grid[next_tile.y][next_tile.x] in const.BAD_TILES:
            next_tile = tile

        # Chooses target tile depending on movement direction
        if self.state.direction.y != 0:
            target = Vector(tile.x, next_tile.y) * const.TILE_SIZE
        elif self.state.direction.x != 0:
            target = Vector(next_tile.x, tile.y) * const.TILE_SIZE
        else:
            target = self.state.position

        # Linearly interpolate to target tile.
        self.state.position.lerp(target, self.state.speed)

    def reset(self, position: Optional[Vector] = None) -> None:
        """Reset the actor to a default state.

        Args:
            - position: The position the actor can be reset to.
        """
        if position is None:
            self.reset_position()
        else:
            self.state.position = copy(position)

        self.reset_direction()
        self.reset_colour()
        self.reset_speed()

    def reset_position(self) -> None:
        """Reset position to the default. """
        self.state.position = copy(self._default_state.position)

    def reset_direction(self) -> None:
        """Reset direction to the default. """
        self.state.direction = self._default_state.direction
        self._queued_direction = None

    def reset_colour(self) -> None:
        """Reset colour to the default. """
        self.state.colour = self._default_state.colour

    def reset_speed(self) -> None:
        """Reset speed to the default. """
        self.state.speed = self._default_state.speed

    def draw(self, screen: pygame.Surface, is_debug: bool = False) -> None:
        """Draws the actor onto the pygame screen.

        Args:
            - screen: The pygame screen used for drawing onto.
            - is_debug: Whether to draw debug information or not.
        """
        if is_debug:
            # Draws current tile.
            tile_position = self.tile() * const.TILE_SIZE
            pygame.draw.rect(screen, (100, 100, 0), pygame.Rect(*tile_position, *const.TILE_SIZE))

            # Draws next tile.
            next_position = (self.tile() + self.state.direction) * const.TILE_SIZE
            pygame.draw.rect(screen, (100, 0, 0), pygame.Rect(*next_position, *const.TILE_SIZE))

            # Draws a yellow line representing current direction.
            start_position = self.state.position + 8
            end_direction = start_position + self.state.direction * 20
            pygame.draw.line(screen, (200, 200, 0), start_position.tuple(),
                             end_direction.tuple(), 4)

            # Draws a red line representing the queued direction
            if self._queued_direction is not None:
                end_queue_dir = start_position + self._queued_direction * 20
                pygame.draw.line(screen, (200, 50, 0), start_position.tuple(),
                                 end_queue_dir.tuple(), 4)

        # Draw actor.
        pygame.draw.rect(screen, self.state.colour, self.rect())


class TimerState:
    """A class representing a game's timers and other timing elements.

    Instance Attributes:
        - mode_level: The level of game's current mode, between chase and scatter.
        - round_timer: Timer used to cycle between modes.
        - start_timer: Timer used for the pause at start of rounds.
        - release_level: The level of ghost release, each level represents another ghost release.
        - release_timer: Timer used to release the ghosts.
        - boost_level: The level of the boost point bonus.
        - boost_timer: Timer used to set length of boost state.
    """
    mode_level: int
    round_timer: int
    start_timer: int

    release_level: int
    release_timer: int

    boost_level: int
    boost_timer: int

    def __init__(self) -> None:
        """Initializes timers to their initial states. """
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
        """Updates all timer states accordingly. """
        # Update ghost release
        if self.release_timer >= const.GHOST_RELEASE:
            self.release_timer = 0
            self.release_level += 1
        elif self.release_level < 3:
            self.release_timer += 1

        # Update boost timer
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
        """Reset the start timer to its initial state. """
        self.start_timer = const.ROUND_START

    def check_start(self) -> bool:
        """Returns whether or not start timer is still active. If it is, update its state. """
        if pygame.display.get_init() and self.start_timer > 0:
            self.start_timer -= 1
            return True
        else:
            return False

    def set_release(self) -> None:
        """Reset the ghost release timers to their initial states. """
        self.release_timer = 0
        self.release_level = 0

    def set_boost(self) -> None:
        """Reset the boost timers to their initial states. """
        self.boost_timer = const.BOOST_TIME
        self.boost_level = 0

    def check_boost(self) -> bool:
        """Returns whether or not boost is still active. """
        return self.boost_timer <= 0


class GameState:
    """A class representing a game's current state.

    Instance Attributes:
        - controllers: The list of all controllers used in game.
        - events: The list of game input events.
        - lost_life: Whether or not the player has lost a life yet.
        - lives: The amount of lives the player has.
        - score: The current game state's score.
        - dot_counter: The amount of dots the player has eaten.
        - timers: The timer states for the game.

    Representation Invariants:
        - self.score >= 0
        - self.dot_counter >= 0

        - Player is the last element in self.controllers
    """
    controllers: list[game_controls.Controller]
    events: Optional[list[pygame.event.Event]]

    lost_life: bool
    lives: int
    score: int
    dot_counter: int

    timers: TimerState

    def __init__(self, lives: int) -> None:
        """Initializes the game state with amount of initial lives.

        Args:
            - lives: The initial amount of lives the player has.
        """
        self.controllers = []
        self.events = None

        self.lost_life = False
        self.lives = lives
        self.score = 0

        self.dot_counter = 0
        self.timers = TimerState()

    def player(self) -> game_controls.Controller:
        """Returns the player's controller, using the representation invariant. """
        return self.controllers[-1]

    def player_actor(self) -> Actor:
        """Returns the player's actor, using the representation invariant. """
        return self.controllers[-1].actor

    def ghosts(self) -> list[game_controls.GhostController]:
        """Returns a list of the ghosts' controllers, given the representation invariant. """
        return self.controllers[:-1]

    def ghosts_actor(self) -> list[Actor]:
        """Returns a list of the ghosts' actors, given the representation invariant. """
        return [control.actor for control in self.controllers[:-1]]

    def mode(self) -> str:
        """Returns the game's mode, either chase or scatter. """
        return const.ROUND_PATTERN[self.timers.mode_level][1]


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['copy', 'dataclasses', 'pygame', 'game_constants', 'game_controls',
                          'helpers', 'vector'],
        'max-line-length': 100,
        'disable': ['E1136']
    })

    import python_ta.contracts
    python_ta.contracts.DEBUG_CONTRACTS = False
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()
