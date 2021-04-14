from typing import Optional
import pygame

from ai_neural_net import NeuralNetGraph
from game_state import Actor, GameState
from helpers import within_grid
from vector import Vector

import ai_constants as ai_const
import game_constants as g_const
import controls


class AIController(controls.Controller):
    neural_net: Optional[NeuralNetGraph]
    ticks_alive: int
    last_score: tuple[int, int]

    def __init__(self, game: GameState, actor: Actor,
                 neural_net: Optional[NeuralNetGraph] = None) -> None:
        super().__init__(game, actor)
        self.neural_net = neural_net

        self.ticks_alive = 0
        self.last_score = (0, self.ticks_alive)

    def control(self, grid: list[list[int]]) -> None:
        directions = list(ai_const.DIRECTION_ROTATE)

        dir_index = directions.index(self.actor.state.direction)
        end_index = dir_index + len(directions) // 2
        directions = directions[dir_index: end_index]

        # Propagate through neural network
        self.get_inputs(grid, directions)
        self.control_outputs(directions)

        # Checks if player has been inactive
        self.ticks_alive += 1

        if self.game.score != self.last_score[0]:
            self.last_score = (self.game.score, self.ticks_alive)
        elif self.ticks_alive - self.last_score[1] > ai_const.POINT_TIMEOUT:
            self.game.lives = 0

    def get_inputs(self, grid: list[list[int]], directions: list[Vector]) -> None:
        out = []
        tile = self.actor.tile()
        target_tiles = {g_const.WALL, g_const.DOOR, g_const.OUT, g_const.DOT, g_const.BOOST}

        for direction in directions:
            next_tile = tile + direction

            # Check if can move in this direction
            if not within_grid(next_tile) or grid[next_tile.y][next_tile.x] in g_const.BAD_TILES:
                out.append(ai_const.ACTIVE)
                out.append(ai_const.INACTIVE)
                continue
            else:
                out.append(ai_const.INACTIVE)

            # Check if score can be increased in this direction
            while grid[next_tile.y][next_tile.x] not in target_tiles:
                next_tile += direction

            if grid[next_tile.y][next_tile.x] in g_const.BAD_TILES:
                out.append(ai_const.INACTIVE)
            else:
                out.append(ai_const.ACTIVE)

        print(out)

    def control_outputs(self, directions: list[Vector]) -> None:
        pass

    def draw_debug(self, screen: pygame.Surface) -> None:
        pass


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['pygame', 'ai_constants', 'ai_neural_net', 'controls', 'game_constants',
                          'game_state', 'helpers', 'vector'],
        'max-line-length': 100,
        'disable': ['E1136']
    })

    import python_ta.contracts
    python_ta.contracts.DEBUG_CONTRACTS = True
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()
