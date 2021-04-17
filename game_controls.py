"""CSC111 Final Project

Module containing the controller classes used to move the actors in PacMan.
"""
from typing import Optional
import random
import pygame

from game_state import Actor, GameState
from helpers import grid_distance, within_grid
from vector import Vector
import game_constants as const


class Controller:
    """A class representing a controller for an actor.

    Instance Attributes:
        - game: The game the controller is running in.
        - actor: The actor associated with this controller.
    """
    game: GameState
    actor: Actor

    def __init__(self, game: GameState, actor: Actor) -> None:
        """Initializes a new controller with given game and actor.

        Args:
            - game: The game the controller is running in.
            - actor: The actor associated with this controller.
        """
        self.game = game
        self.actor = actor

        game.controllers.append(self)

    def control(self, grid: list[list[int]]) -> None:
        """Controls the actor for given tick.

        Args:
            - grid: The current game's map grid.
        """
        raise NotImplementedError

    def reset(self) -> None:
        """Resets the controller for when associated actor dies."""
        raise NotImplementedError

    def draw_debug(self, screen: pygame.Surface) -> None:
        """Draws out debugging information.

        Args:
            - screen: The pygame game screen.
        """
        raise NotImplementedError


class InputController(Controller):
    """A class representing a controller for an actor which uses keyboard input. """

    def control(self, grid: list[list[int]]) -> None:
        """Controls the actor for given tick using keyboard input.

        Args:
            - grid: The current game's map grid.
        """
        if self.game.events is None:
            return

        # Changes direction based on key presses
        for event in self.game.events:
            if event.type == pygame.KEYDOWN:
                self.actor.change_direction(grid, const.DIRECTION.get(event.key))

    def reset(self) -> None:
        """Resets the controller for when associated actor dies. Not needed for this subclass! """

    def draw_debug(self, screen: pygame.Surface) -> None:
        """Draws out debugging information. Not needed for this subclass!

        Args:
            - screen: The pygame game screen.
        """


class GhostController(Controller):
    """A class representing a controller for a ghost actor.

    Instance Attributes:
        - home_timer: The time in ticks until the ghost moves out of home.
        - state: The state of the ghosts. (See Representation Invariants)
        - mode: The mode of active state ghosts. (See Representation Invariants)

    Representation Invariants:
        - self.state in {'inactive', 'home', 'active'}
        - self.mode in {'scatter', 'chase'}
    """
    home_timer: int
    state: str
    mode: str

    # Private Instance Attributes:
    #  - _next_tile : The target tile to arrive to.
    #  - _next_direction: The direction to be turned towards when possible
    #  - _is_frightened : Whether ghost is frightened.
    _next_tile: Optional[Vector]
    _next_direction: Optional[Vector]
    _is_frightened: bool

    def __init__(self, game: GameState, actor: Actor) -> None:
        """Initializes a new ghost controller with given game and ghost actor.

        Args:
            - game: The game the controller is running in.
            - actor: The ghost actor associated with this controller.
        """
        super().__init__(game, actor)
        self._next_tile = None
        self._next_direction = None
        self.home_timer = 0

        self.state = 'inactive'
        self.mode = self.game.mode()
        self._is_frightened = False

    def control(self, grid: list[list[int]]) -> None:
        """Controls the ghost actor for given tick based on current state or mode.

        Args:
            - grid: The current game's map grid.
        """
        if self.state == 'active':
            # Change targeting if there is change in mode
            game_mode = self.game.mode()
            if self.mode != game_mode and not self._is_frightened:
                self._next_tile = None
                self._next_direction = None
                self.actor.reset_direction()

                self.mode = game_mode

            # Check if target tile has been reached, or if it is unreachable.
            tile = self.actor.tile()
            if self._next_tile is not None and grid_distance(self._next_tile, tile) > 1:
                self._next_tile = None
            elif self._next_tile is not None and tile != self._next_tile:
                return

            # Change the queued direction.
            self.actor.change_direction(grid, self._next_direction)

            # Choose new next tile.
            if self._next_tile is None:
                self._next_tile = tile
            else:
                self._next_tile = tile + self._next_direction

            # Control differently depending on frightened state
            if not self._is_frightened:
                self.control_target(grid)
            else:
                self.control_fright(grid)
        elif self.state == 'home':
            self.control_home()
        elif self.state == 'inactive' and self.check_active():
            # If activated, change to home state
            self.state = 'home'

    def control_target(self, grid: list[list[int]]) -> None:
        """Controls the ghost actor for given tick if in targeting mode.
        Follows the original ghost targeting system closely!

        Args:
            - grid: The current game's map grid.
        """
        self._next_direction = -self.actor.state.direction
        best_distance = None

        # Try each direction.
        for key in const.DIRECTION_ORDER:
            direction = const.DIRECTION[key]
            candidate = self._next_tile + direction

            # If can't turn in this direction.
            if not within_grid(candidate) or candidate == self.actor.tile() or \
                    grid[candidate.y][candidate.x] in const.BAD_TILES:
                continue

            # Target different things depending on mode.
            if self.mode == 'scatter':
                distance = grid_distance(candidate, self.scatter_target())
            else:  # Chase mode case by representation invariant.
                distance = grid_distance(candidate, self.chase_target())

            # Choose this direction if shortest so far.
            if best_distance is None or distance < best_distance:
                self._next_direction = direction
                best_distance = distance

    def control_fright(self, grid: list[list[int]]) -> None:
        """Controls the ghost actor for given tick if frightened.
        When frightened, it turns a random direction at each intersection.

        Args:
            - grid: The current game's map grid.
        """
        # Collect all possible directions at intersection.
        candidates = []
        for key in const.DIRECTION_ORDER:
            direction = const.DIRECTION[key]
            candidate = self._next_tile + direction

            # Can't turn in this direction.
            if within_grid(candidate) and candidate != self.actor.tile() and \
                    grid[candidate.y][candidate.x] not in const.BAD_TILES:
                candidates.append(direction)

        # Randomly choose direction from allowed directions.
        if candidates != []:
            self._next_direction = random.choice(candidates)
        else:
            self._next_direction = -self.actor.state.direction

    def control_home(self) -> None:
        """Controls the ghost actor for given tick if in home state.
        When wait until home timer is over, then moves outside of ghost home.

        Args:
            - grid: The current game's map grid.
        """
        # Increment ghost timer.
        if self.home_timer > 0:
            self.home_timer -= 1
            return

        actor_pos = self.actor.state.position

        # Move out of ghost house.
        if actor_pos == const.DEFAULT_POS:
            self.state = 'active'
        elif actor_pos.x == const.DEFAULT_POS.x:
            actor_pos.lerp(const.DEFAULT_POS, self.actor.state.speed)
        else:
            actor_pos.lerp(const.GHOST_POS[1], self.actor.state.speed)

    def set_frightened(self, is_frightened: bool) -> None:
        """Sets whether or not ghost controller is in a frightened mode.

        Args:
            - is_frightened: Whether ghost is frightened or not.
        """
        if not self._is_frightened and is_frightened:
            # Set frightened state.
            self.actor.state.colour = const.FRIGHT
            self.actor.state.speed *= 0.5
            self.mode = ''
        elif self._is_frightened and not is_frightened:
            # Reset to non-frightened state.
            self.actor.reset_colour()
            self.actor.reset_speed()
            self.mode = ''

        self._is_frightened = is_frightened

    def get_frightened(self) -> bool:
        """Returns if ghost controller is in a frightened mode."""
        return self._is_frightened

    def reset(self) -> None:
        """Resets the controller targeting for when associated actor dies. """
        self._next_tile = None
        self._next_direction = None

        self.mode = self.game.mode()
        self.home_timer = 0

    def draw_debug(self, screen: pygame.Surface) -> None:
        """Draws out debugging information for ghost controller.

        Args:
            - screen: The pygame game screen.
        """
        if self.state != 'active' or self.mode == 'fright' or self._next_tile is None:
            return

        # Draw desired next position.
        next_position = self._next_tile * const.TILE_SIZE
        pygame.draw.rect(screen, (100, 0, 100), pygame.Rect(*next_position, *const.TILE_SIZE))

        # Draw target tile depending on mode
        if self.game.mode() == 'scatter':
            target_position = self.scatter_target() * const.TILE_SIZE
        else:  # Chase mode case
            target_position = self.chase_target() * const.TILE_SIZE

        pygame.draw.rect(screen, (0, 100, 100), pygame.Rect(*target_position, *const.TILE_SIZE))

    def scatter_target(self) -> Vector:
        """Returns the target tile during scatter mode. """
        raise NotImplementedError

    def chase_target(self) -> Vector:
        """Returns the target tile during chase mode. """
        raise NotImplementedError

    def check_active(self) -> bool:
        """Returns whether or not the ghost controller will be reactivate. """
        raise NotImplementedError


class BlinkyController(GhostController):
    """A class representing a controller for the ghost Blinky. """

    def __init__(self, game: GameState, actor: Actor) -> None:
        """Initializes a new ghost controller with given game and ghost actor.
        Specifically, this is Blinky, the red ghost!

        Args:
            - game: The game the controller is running in.
            - actor: The ghost actor associated with this controller.
        """
        super().__init__(game, actor)
        self.state = 'active'

    def reset(self) -> None:
        """Resets the controller targeting for when associated actor dies.
        Blinky starts off active.
        """
        super().reset()
        self.state = 'active'

    def scatter_target(self) -> Vector:
        """Returns the target tile during scatter mode, the top right corner. """
        return Vector(25, 0)

    def chase_target(self) -> Vector:
        """Returns the target tile during chase mode, PacMan itself! """
        return self.game.player_actor().tile()

    def check_active(self) -> bool:
        """Returns whether or not the ghost controller will be reactivate.
        Blinky is always active!
        """
        return True


class PinkyController(GhostController):
    """A class representing a controller for the ghost Pinky. """

    def __init__(self, game: GameState, actor: Actor) -> None:
        """Initializes a new ghost controller with given game and ghost actor.
        Specifically, this is Pinky, the pink ghost! (As the name suggests...)

        Args:
            - game: The game the controller is running in.
            - actor: The ghost actor associated with this controller.
        """
        super().__init__(game, actor)
        self.state = 'home'

    def reset(self) -> None:
        """Resets the controller targeting for when associated actor dies.
        Pinky starts off inactive.
        """
        super().reset()
        self.state = 'inactive'

    def scatter_target(self) -> Vector:
        """Returns the target tile during scatter mode, the top left corner. """
        return Vector(2, 0)

    def chase_target(self) -> Vector:
        """Returns the target tile during chase mode, 4 tiles ahead of PacMan. """
        player = self.game.player_actor()

        if player.state.direction != const.DIRECTION[pygame.K_UP]:
            return player.tile() + 4 * player.state.direction
        else:
            # Replicates the original bug with Pinky's up-targeting
            return player.tile() + (-4, -4)

    def check_active(self) -> bool:
        """Returns whether or not the ghost controller will be reactivate.
        Depends on initial release level or dot threshold.
        """
        if self.game.timers.release_level >= 1:
            return True

        if self.game.lost_life:
            return self.game.dot_counter >= 7
        else:
            return True


class InkyController(GhostController):
    """A class representing a controller for the ghost Inky. """

    def __init__(self, game: GameState, actor: Actor) -> None:
        """Initializes a new ghost controller with given game and ghost actor.
        Specifically, this is Inky, the teal ghost!

        Args:
            - game: The game the controller is running in.
            - actor: The ghost actor associated with this controller.
        """
        super().__init__(game, actor)
        self.state = 'inactive'

    def reset(self) -> None:
        """Resets the controller targeting for when associated actor dies.
        Inky starts off inactive.
        """
        super().reset()
        self.state = 'inactive'

    def scatter_target(self) -> Vector:
        """Returns the target tile during scatter mode, the bottom right corner. """
        return Vector(27, 35)

    def chase_target(self) -> Vector:
        """Returns the target tile during chase mode, which is opposite of Blinky's position
        relative to PacMan.
        """
        # Note the original bug with Inky's up-targeting is ignored as effect is insignificant
        player = self.game.player_actor()
        pivot = player.tile() + 2 * player.state.direction

        return pivot - (self.game.controllers[0].actor.tile() - pivot)

    def check_active(self) -> bool:
        """Returns whether or not the ghost controller will be reactivate.
        Depends on initial release level or dot threshold.
        """
        if self.game.timers.release_level >= 2:
            return True

        if not self.game.lost_life:
            return self.game.dot_counter >= 30
        else:
            return self.game.dot_counter >= 17


class ClydeController(GhostController):
    """A class representing a controller for the ghost Clyde. """

    def __init__(self, game: GameState, actor: Actor) -> None:
        """Initializes a new ghost controller with given game and ghost actor.
        Specifically, this is Clyde, the orange ghost!
        Why is he named different? Who knows!

        Args:
            - game: The game the controller is running in.
            - actor: The ghost actor associated with this controller.
        """
        super().__init__(game, actor)
        self.state = 'inactive'

    def reset(self) -> None:
        """Resets the controller targeting for when associated actor dies.
        Clyde starts off inactive.
        """
        super().reset()
        self.state = 'inactive'

    def scatter_target(self) -> Vector:
        """Returns the target tile during scatter mode, the bottom left corner. """
        return Vector(0, 35)

    def chase_target(self) -> Vector:
        """Returns the target tile during chase mode, which PacMan itself, unless Clyde is within
        8 tiles of PacMan, for which it uses its scatter target.
        """
        player_tile = self.game.player_actor().tile()

        if grid_distance(self.actor.tile(), player_tile) > 8:
            return player_tile
        else:
            return Vector(0, 35)

    def check_active(self) -> bool:
        """Returns whether or not the ghost controller will be reactivate.
        Depends on initial release level or dot threshold.
        """
        if self.game.timers.release_level >= 3:
            return True

        if not self.game.lost_life:
            return self.game.dot_counter >= 60
        else:
            return self.game.dot_counter >= 32


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['random', 'pygame', 'game_constants', 'game_state',
                          'helpers', 'vector'],
        'max-line-length': 100,
        'disable': ['E1136', 'E1101']
    })

    import python_ta.contracts
    python_ta.contracts.DEBUG_CONTRACTS = False
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()
