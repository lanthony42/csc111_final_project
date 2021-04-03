from __future__ import annotations

from typing import Optional, TYPE_CHECKING
import random
import pygame

from helpers import grid_distance, within_grid
from vector import Vector
import constants as const

# Only imports when type-checking to avoid circular import issues
if TYPE_CHECKING:
    import game


class Controller:
    game_state: game.Game
    actor: game.Actor

    def __init__(self, game_state: game.Game, actor: game.Actor) -> None:
        self.game_state = game_state
        self.actor = actor

    def control(self) -> None:
        raise NotImplementedError

    def draw_debug(self) -> None:
        raise NotImplementedError


class InputController(Controller):
    def control(self) -> None:
        if self.game_state.events is None:
            return

        for event in self.game_state.events:
            if event.type == pygame.KEYDOWN:
                self.actor.change_direction(self.game_state.grid, const.DIRECTION.get(event.key))

    def draw_debug(self) -> None:
        pass


class GhostController(Controller):
    _next_tile: Optional[Vector]
    _next_direction: Optional[Vector]
    _is_frightened: bool

    state: str
    mode: str

    def __init__(self, game_state: game.Game, actor: game.Actor) -> None:
        super().__init__(game_state, actor)
        self._next_tile = None
        self._next_direction = None

        # self.state in {'inactive', 'home', 'active'}
        self.state = 'inactive'
        # self.mode in {'scatter', 'chase'}
        self.mode = self.game_state.mode()
        self._is_frightened = False

    def control(self) -> None:
        if self.state == 'active':
            game_mode = self.game_state.mode()
            if self.mode != game_mode and not self._is_frightened:
                self._next_tile = None
                self._next_direction = None
                self.actor.reset_direction()

                self.mode = game_mode

            tile = self.actor.tile()
            if self._next_tile is not None and grid_distance(self._next_tile, tile) > 1:
                self._next_tile = None
            elif self._next_tile is not None and tile != self._next_tile:
                return

            self.actor.change_direction(self.game_state.grid, self._next_direction)

            if self._next_tile is None:
                self._next_tile = tile
            else:
                self._next_tile = tile + self._next_direction

            if not self._is_frightened:
                self.control_target()
            else:
                self.control_fright()
        elif self.state == 'home':
            self.control_home()
        elif self.state == 'inactive' and self.check_active():
            self.state = 'home'

    def control_target(self) -> None:
        self._next_direction = -self.actor.direction
        best_distance = None

        for key in const.DIRECTION_ORDER:
            direction = const.DIRECTION[key]
            candidate = self._next_tile + direction

            if not within_grid(candidate) or candidate == self.actor.tile() or \
                    self.game_state.grid[candidate.y][candidate.x] in const.BAD_TILES:
                continue

            if self.mode == 'scatter':
                distance = grid_distance(candidate, self.scatter_target())
            else:
                # Chase mode case
                distance = grid_distance(candidate, self.chase_target())

            if best_distance is None or distance < best_distance:
                self._next_direction = direction
                best_distance = distance

    def control_fright(self) -> None:
        candidates = []
        for key in const.DIRECTION_ORDER:
            direction = const.DIRECTION[key]
            candidate = self._next_tile + direction

            if within_grid(candidate) and candidate != self.actor.tile() and \
                    self.game_state.grid[candidate.y][candidate.x] not in const.BAD_TILES:
                candidates.append(direction)

        if candidates != []:
            self._next_direction = random.choice(candidates)
        else:
            self._next_direction = -self.actor.direction

    def control_home(self) -> None:
        actor_pos = self.actor.position

        if actor_pos == const.DEFAULT_POS:
            self.state = 'active'
        elif actor_pos.x == const.DEFAULT_POS.x:
            self.actor.position.lerp(const.DEFAULT_POS, self.actor.speed)
        else:
            self.actor.position.lerp(const.GHOST_POS[1], self.actor.speed)

    def set_frightened(self, is_frightened: bool) -> None:
        if not self._is_frightened and is_frightened:
            self.actor.colour = const.FRIGHT
            self.actor.speed *= 0.5
            self.mode = ''
        elif self._is_frightened and not is_frightened:
            self.actor.reset_colour()
            self.actor.reset_speed()
            self.mode = ''

        self._is_frightened = is_frightened

    def get_frightened(self) -> bool:
        return self._is_frightened

    def reset(self) -> None:
        self._next_tile = None
        self._next_direction = None

        self.mode = self.game_state.mode()

    def draw_debug(self) -> None:
        if self.state != 'active' or self.mode == 'fright' or self._next_tile is None:
            return

        next_position = self._next_tile * const.TILE_SIZE
        pygame.draw.rect(self.game_state.screen, (100, 0, 100),
                         pygame.Rect(*next_position, *const.TILE_SIZE))

        if self.game_state.mode() == 'scatter':
            target_position = self.scatter_target() * const.TILE_SIZE
        else:
            # Chase mode case
            target_position = self.chase_target() * const.TILE_SIZE

        pygame.draw.rect(self.game_state.screen, (0, 100, 100),
                         pygame.Rect(*target_position, *const.TILE_SIZE))

    def scatter_target(self) -> Vector:
        raise NotImplementedError

    def chase_target(self) -> Vector:
        raise NotImplementedError

    def check_active(self) -> bool:
        raise NotImplementedError


class BlinkyController(GhostController):
    def __init__(self, game_state: game.Game, actor: game.Actor) -> None:
        super().__init__(game_state, actor)
        self.state = 'active'

    def reset(self) -> None:
        super().reset()
        self.state = 'active'

    def scatter_target(self) -> Vector:
        return Vector(25, 0)

    def chase_target(self) -> Vector:
        return self.game_state.player.actor.tile()

    def check_active(self) -> bool:
        return True


class PinkyController(GhostController):
    def __init__(self, game_state: game.Game, actor: game.Actor) -> None:
        super().__init__(game_state, actor)
        self.state = 'home'

    def reset(self) -> None:
        super().reset()
        self.state = 'inactive'

    def scatter_target(self) -> Vector:
        return Vector(2, 0)

    def chase_target(self) -> Vector:
        player = self.game_state.player.actor

        if player.direction != const.DIRECTION[pygame.K_UP]:
            return player.tile() + 4 * player.direction
        else:
            # Replicates the original bug with Pinky's up-targeting
            return player.tile() + (-4, -4)

    def check_active(self) -> bool:
        if self.game_state.release_level >= 1:
            return True

        if self.game_state.lost_life:
            return self.game_state.dot_counter >= 7
        else:
            return True


class InkyController(GhostController):
    def __init__(self, game_state: game.Game, actor: game.Actor) -> None:
        super().__init__(game_state, actor)
        self.state = 'inactive'

    def reset(self) -> None:
        super().reset()
        self.state = 'inactive'

    def scatter_target(self) -> Vector:
        return Vector(27, 35)

    def chase_target(self) -> Vector:
        # Note the original bug with Inky's up-targeting is ignored as effect is insignificant
        player = self.game_state.player.actor
        pivot = player.tile() + 2 * player.direction

        return pivot - (self.game_state.ghosts[0].actor.tile() - pivot)

    def check_active(self) -> bool:
        if self.game_state.release_level >= 2:
            return True

        if not self.game_state.lost_life:
            return self.game_state.dot_counter >= 30
        else:
            return self.game_state.dot_counter >= 17


class ClydeController(GhostController):
    def __init__(self, game_state: game.Game, actor: game.Actor) -> None:
        super().__init__(game_state, actor)
        self.state = 'inactive'

    def reset(self) -> None:
        super().reset()
        self.state = 'inactive'

    def scatter_target(self) -> Vector:
        return Vector(0, 35)

    def chase_target(self) -> Vector:
        player_tile = self.game_state.player.actor.tile()

        if grid_distance(self.actor.tile(), player_tile) > 8:
            return player_tile
        else:
            return Vector(0, 35)

    def check_active(self) -> bool:
        if self.game_state.release_level >= 3:
            return True

        if not self.game_state.lost_life:
            return self.game_state.dot_counter >= 60
        else:
            return self.game_state.dot_counter >= 32


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['random', 'pygame', 'constants', 'game', 'helpers', 'vector'],
        'max-line-length': 100,
        'disable': ['E1136', 'E1101']
    })

    import python_ta.contracts
    python_ta.contracts.DEBUG_CONTRACTS = True
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()
