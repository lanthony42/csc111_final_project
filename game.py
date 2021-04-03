from copy import copy, deepcopy
from typing import Type, Optional
import csv
import pygame

from helpers import Vector, within_grid
import constants as const
import controls


class Game:
    def __init__(self, map_path: str) -> None:
        self.clock = pygame.time.Clock()
        self.screen = None
        self.events = None
        self.font = None

        self.ghosts = []
        self.player = None

        self.game_over = False
        self.lost_life = False
        self.lives = 0
        self.score = 0

        # Round variables
        self._mode_ind = 0
        self._round_timer = const.ROUND_PATTERN[self._mode_ind][0]
        self._start_timer = const.ROUND_START

        self.dot_counter = 0
        self.release_timer = 0
        self.release_level = 0
        self.boost_timer = 0
        self.boost_ind = 0

        # Load the map
        with open(map_path) as csv_file:
            reader = csv.reader(csv_file)
            self._base_grid = list(reader)
        self.grid = []

    def mode(self) -> str:
        return const.ROUND_PATTERN[self._mode_ind][1]

    def run(self, player_controller: Type[controls.Controller] = controls.InputController,
            lives: int = const.DEFAULT_LIVES, visual: bool = True, debug: bool = False) -> int:
        # Reinitialize
        self.player = player_controller(self, Actor(position=const.PLAYER_POS,
                                                    direction=const.PLAYER_DIR,
                                                    speed=const.PLAYER_SPEED))

        controllers = (controls.BlinkyController, controls.PinkyController,
                       controls.InkyController, controls.ClydeController)
        self.ghosts = [control(self, Actor(position=pos, colour=col, cornering=False))
                       for control, pos, col in zip(controllers, const.GHOST_POS,
                                                    const.GHOST_COLOURS)]
        self.grid = deepcopy(self._base_grid)

        self.events = None
        self.game_over = False
        self.lost_life = False

        self.lives = lives
        self.score = 0

        # Round variables
        self._mode_ind = 0
        self._round_timer = const.ROUND_PATTERN[self._mode_ind][0]
        self._start_timer = const.ROUND_START

        self.dot_counter = 0
        self.release_timer = 0
        self.release_level = 0
        self.boost_timer = 0
        self.boost_ind = 0

        # Set up screen
        if visual and not pygame.display.get_init():
            pygame.init()

            self.screen = pygame.display.set_mode(const.SCREEN_SIZE.tuple())
            self.font = pygame.font.SysFont('arial', 24)
            pygame.display.set_caption('Pac-Man')
        elif not visual:
            self.screen = None
            self._start_timer = 0

        # Start game loop
        while not self.game_over:
            if self.handle_input():
                break

            self.update()

            if visual:
                self.draw(debug)
                self.clock.tick(const.FPS)

        return {'game_win': self.check_win(), 'score': self.score}

    def handle_input(self) -> bool:
        if not pygame.display.get_init():
            return False

        self.events = pygame.event.get()

        for event in self.events:
            if event.type == pygame.KEYDOWN:
                self._start_timer = 0
            elif event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()

                return True
        return False

    def update(self) -> None:
        # Check for start timer
        if self._start_timer > 0:
            self._start_timer -= 1
            return

        # Update other timers
        self.update_timers()

        # Control and update actors
        self.player.control()
        self.player.actor.update(self.grid)

        for ghost in self.ghosts:
            if self.boost_timer <= 0:
                ghost.set_frightened(False)

            ghost.control()
            ghost.actor.update(self.grid)

            # Ghost collisions
            is_collide = self.player.actor.rect().colliderect(ghost.actor.rect())
            if is_collide and ghost.get_frightened():
                ghost.set_frightened(False)
                ghost.state = 'home'

                ghost.actor.reset(const.HOME_POS)

                self.score += const.GHOST_SCORE[self.boost_ind]
                self.boost_ind += 1
            elif is_collide:
                self.lose_life()
                break

        # Tile collisions
        tile = self.player.actor.tile()
        if self.grid[tile.y][tile.x] == const.DOT:
            self.grid[tile.y][tile.x] = const.EMPTY
            self.score += const.DOT_SCORE
            self.dot_counter += 1
        elif self.grid[tile.y][tile.x] == const.BOOST:
            self.grid[tile.y][tile.x] = const.EMPTY
            self.score += const.BOOST_SCORE

            self.boost_timer = const.BOOST_TIME
            self.boost_ind = 0

            for ghost in self.ghosts:
                ghost.set_frightened(True)

        # Check win and lose conditions
        if self.lives <= 0 or self.check_win():
            self.game_over = True

    def update_timers(self) -> None:
        if self.release_timer >= const.GHOST_RELEASE:
            self.release_timer = 0
            self.release_level += 1
        elif self.release_level < 3:
            self.release_timer += 1

        if self.boost_timer > 0:
            self.boost_timer -= 1

        # Update round pattern
        if self._round_timer is not None:
            if self._round_timer <= 0:
                self._mode_ind += 1
                self._round_timer = const.ROUND_PATTERN[self._mode_ind][0]
            else:
                self._round_timer -= 1

    def lose_life(self) -> None:
        self.lost_life = True
        self.dot_counter = 0
        self.release_timer = 0
        self.release_level = 0
        self.lives -= 1

        for ghost in self.ghosts:
            ghost.reset()
            ghost.actor.reset()

        self.player.actor.reset()

        if pygame.display.get_init():
            self._start_timer = const.ROUND_START

    def draw(self, debug: bool = False) -> None:
        self.screen.fill((0, 0, 0))

        for y, row in enumerate(self.grid):
            for x, tile in enumerate(row):
                self.draw_tile(tile, x, y, debug)

        if debug:
            self.draw_debug()

        for ghost in self.ghosts:
            ghost.actor.draw(self.screen, debug)

        self.player.actor.draw(self.screen, debug)

        self.screen.blit(self.font.render(f'Score: {self.score}', 1,
                                          (255, 255, 255)), (5, 5))
        pygame.display.update()

    def draw_debug(self) -> None:
        for ghost in self.ghosts:
            ghost.draw_debug()

        self.player.draw_debug()

    def draw_tile(self, tile: str, x: int, y: int, debug: bool = False) -> None:
        position = const.TILE_SIZE * (x, y)

        if tile == const.WALL:
            pygame.draw.rect(self.screen, (0, 0, 255), pygame.Rect(*position, *const.TILE_SIZE))
        elif tile == const.DOOR:
            pygame.draw.rect(self.screen, (255, 150, 200), pygame.Rect(*position, *const.TILE_SIZE))
        elif tile == const.DOT:
            pygame.draw.circle(self.screen, (200, 200, 150),
                               (position + const.TILE_SIZE / 2).tuple(), 2)
        elif tile == const.BOOST:
            pygame.draw.circle(self.screen, (220, 220, 220),
                               (position + const.TILE_SIZE / 2).tuple(), 5)

        if debug:
            pygame.draw.rect(self.screen, (100, 100, 100),
                             pygame.Rect(*position, *const.TILE_SIZE), width=1)

    def check_win(self) -> None:
        return not any(tile in {const.DOT, const.BOOST} for row in self.grid for tile in row)


class Actor:
    def __init__(self, position: Vector = const.DEFAULT_POS, direction: Vector = Vector(0, 0),
                 speed: float = const.DEFAULT_SPEED, colour: tuple[int, int, int] = const.YELLOW,
                 cornering: bool = True) -> None:
        self.position = copy(position)
        self.direction = direction

        self._default_position = position
        self._default_direction = direction
        self._queued_direction = None
        self._default_colour = colour
        self._default_speed = speed

        self.cornering = cornering
        self.colour = colour
        self.speed = speed

    def tile(self) -> Vector:
        return round(self.position / const.TILE_SIZE)

    def rect(self) -> pygame.Rect:
        return pygame.Rect(*self.position, *const.TILE_SIZE)

    def change_direction(self, grid: list[list[int]], direction: Vector) -> None:
        if direction in const.DIRECTION.values():
            tile = self.tile()
            next_tile = tile + direction

            if self.cornering:
                cornering = const.CORNER.get(self.direction.int_tuple())
            else:
                cornering = (-self.speed / 2, self.speed / 2)

            if self.direction.y != 0:
                target = tile.y * const.TILE_SIZE.y
                within_cornering = (target + cornering[0] < self.position.y
                                    < target + cornering[1])
            elif self.direction.x != 0:
                target = tile.x * const.TILE_SIZE.x
                within_cornering = (target + cornering[0] < self.position.x
                                    < target + cornering[1])
            else:
                within_cornering = True
            same_axis = abs(self.direction.x) == abs(direction.x)

            if within_grid(next_tile) and (within_cornering or same_axis) and \
                    grid[next_tile.y][next_tile.x] not in const.BAD_TILES:
                self.direction = direction
                self._queued_direction = None
            else:
                self._queued_direction = direction

    def update(self, grid: list[list[int]]) -> None:
        if self._queued_direction is not None:
            self.change_direction(grid, self._queued_direction)

        tile = self.tile()
        next_tile = self.tile() + self.direction

        if not within_grid(next_tile) or grid[next_tile.y][next_tile.x] in const.BAD_TILES:
            next_tile = tile

        if self.direction.y != 0:
            target = Vector(tile.x, next_tile.y) * const.TILE_SIZE
        elif self.direction.x != 0:
            target = Vector(next_tile.x, tile.y) * const.TILE_SIZE
        else:
            target = self.position

        self.position.lerp(target, self.speed)

    def reset(self, position: Optional[Vector] = None) -> None:
        if position is None:
            self.reset_position()
        else:
            self.position = copy(position)

        self.reset_direction()
        self.reset_colour()
        self.reset_speed()

    def reset_position(self) -> None:
        self.position = copy(self._default_position)

    def reset_direction(self) -> None:
        self.direction = self._default_direction
        self._queued_direction = None

    def reset_colour(self) -> None:
        self.colour = self._default_colour

    def reset_speed(self) -> None:
        self.speed = self._default_speed

    def draw(self, screen: pygame.Surface, debug: bool = False) -> None:
        if debug:
            tile_position = self.tile() * const.TILE_SIZE
            pygame.draw.rect(screen, (100, 100, 0), pygame.Rect(*tile_position, *const.TILE_SIZE))

            next_position = (self.tile() + self.direction) * const.TILE_SIZE
            pygame.draw.rect(screen, (100, 0, 0), pygame.Rect(*next_position, *const.TILE_SIZE))

            start_position = self.position + 8
            end_direction = start_position + self.direction * 20
            pygame.draw.line(screen, (200, 200, 0), start_position.tuple(),
                             end_direction.tuple(), 4)

            if self._queued_direction is not None:
                end_queue_dir = start_position + self._queued_direction * 20
                pygame.draw.line(screen, (200, 50, 0), start_position.tuple(),
                                 end_queue_dir.tuple(), 4)

        pygame.draw.rect(screen, self.colour, self.rect())


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['copy', 'csv', 'pygame', 'constants', 'controls', 'helpers'],
        'allowed-io': ['__init__'],
        'max-line-length': 100,
        'disable': ['E1136', 'E1101']
    })

    import python_ta.contracts
    python_ta.contracts.DEBUG_CONTRACTS = True
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()
