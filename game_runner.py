from copy import deepcopy
from typing import Type, Optional
import csv
import random
import pygame

from game_state import Actor, ActorState, GameState
from vector import Vector
import game_constants as const
import controls


class Game:
    clock: pygame.time.Clock
    screen: Optional[pygame.Surface]
    font: Optional[pygame.font.Font]
    state: Optional[GameState]
    _default_grid: list[list[int]]
    grid: list[list[int]]

    def __init__(self, map_path: str) -> None:
        self.clock = pygame.time.Clock()
        self.screen = None
        self.font = None
        self.state = None

        # Load the map
        with open(map_path) as csv_file:
            reader = csv.reader(csv_file)
            self._default_grid = list(reader)
        self.grid = []

    def run(self, player_controller: Type[controls.Controller] = controls.InputController,
            seed: int = 111, config: dict = None) -> int:
        # Default configurations
        if config is None:
            config = {}

        lives = config.get('lives', const.DEFAULT_LIVES)
        has_ghosts = config.get('has_ghosts', True)
        has_boosts = config.get('has_boosts', True)
        is_visual = config.get('is_visual', True)
        is_debug = config.get('is_debug', False)
        random.seed(seed)

        # Reinitialize
        self.state = GameState(lives)
        if has_ghosts:
            ghost_states = [ActorState(position, Vector(0, 0), colour, const.DEFAULT_SPEED)
                            for position, colour in zip(const.GHOST_POS, const.GHOST_COLOURS)]

            controls.BlinkyController(self.state, Actor(ghost_states[0], False))
            controls.PinkyController(self.state, Actor(ghost_states[1], False))
            controls.InkyController(self.state, Actor(ghost_states[2], False))
            controls.ClydeController(self.state, Actor(ghost_states[3], False))
        player_controller(self.state, Actor())

        self.grid = deepcopy(self._default_grid)
        if not has_boosts:
            self.grid = [[const.DOT if tile == const.BOOST else tile for tile in row]
                         for row in self.grid]

        # Set up screen
        if is_visual and not pygame.display.get_init():
            pygame.init()

            self.screen = pygame.display.set_mode(const.SCREEN_SIZE.tuple())
            self.font = pygame.font.SysFont('arial', 24)
            pygame.display.set_caption('Pac-Man')
        elif not is_visual:
            self.screen = None

        # Start game loop
        game_over = False
        while not game_over:
            if self.handle_input():
                break

            game_over = self.update()

            if is_visual:
                self.draw(is_debug)
                self.clock.tick(const.FPS)

        return {'game_win': self.check_win(), 'score': self.state.score}

    def handle_input(self) -> bool:
        if not pygame.display.get_init():
            return False

        self.state.events = pygame.event.get()

        for event in self.state.events:
            if event.type == pygame.KEYDOWN:
                self.state.timers.start_timer = 0
            elif event.type == pygame.QUIT:
                return True
        return False

    def update(self) -> bool:
        state = self.state
        # Check for start timer
        if state.timers.check_start():
            return False

        # Update other timers
        state.timers.update()

        # Control and update actors
        state.player().control(self.grid)
        state.player_actor().update(self.grid)

        for ghost in state.ghosts():
            if state.timers.check_boost():
                ghost.set_frightened(False)

            ghost.control(self.grid)
            ghost.actor.update(self.grid)

            # Ghost collisions
            is_collide = state.player_actor().rect().colliderect(ghost.actor.rect())
            if is_collide and ghost.get_frightened():
                ghost.set_frightened(False)
                ghost.state = 'home'

                ghost.actor.reset(const.HOME_POS)

                state.score += const.GHOST_SCORE[state.timers.boost_level]
                state.timers.boost_level += 1
            elif is_collide:
                self.lose_life()
                break

        # Tile collisions
        tile = state.player_actor().tile()
        if self.grid[tile.y][tile.x] == const.DOT:
            self.grid[tile.y][tile.x] = const.EMPTY
            state.score += const.DOT_SCORE
            state.dot_counter += 1
        elif self.grid[tile.y][tile.x] == const.BOOST:
            self.grid[tile.y][tile.x] = const.EMPTY
            state.score += const.BOOST_SCORE
            state.timers.set_boost()

            for ghost in state.ghosts():
                ghost.set_frightened(True)

        # Check win and lose conditions
        if state.lives <= 0 or self.check_win():
            return True
        else:
            return False

    def lose_life(self) -> None:
        state = self.state

        state.lost_life = True
        state.dot_counter = 0
        state.lives -= 1

        state.timers.set_start()
        state.timers.set_release()

        for ghost in state.ghosts():
            ghost.reset()
            ghost.actor.reset()

        state.player_actor().reset()

    def draw(self, is_debug: bool = False) -> None:
        self.screen.fill((0, 0, 0))

        for y, row in enumerate(self.grid):
            for x, tile in enumerate(row):
                self.draw_tile(tile, x, y, is_debug)

        if is_debug:
            self.draw_debug()

        for ghost in self.state.ghosts():
            ghost.actor.draw(self.screen, is_debug)

        self.state.player_actor().draw(self.screen, is_debug)

        self.screen.blit(self.font.render(f'Score: {self.state.score}', 1,
                                          (255, 255, 255)), (5, 5))
        pygame.display.update()

    def draw_debug(self) -> None:
        for ghost in self.state.ghosts():
            ghost.draw_debug(self.screen)

        self.state.player().draw_debug(self.screen)

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


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['copy', 'csv', 'random', 'pygame', 'controls', 'game_constants',
                          'game_state', 'vector'],
        'allowed-io': ['__init__'],
        'max-line-length': 100,
        'disable': ['E1136', 'E1101']
    })

    import python_ta.contracts
    python_ta.contracts.DEBUG_CONTRACTS = True
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()
