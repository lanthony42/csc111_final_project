from copy import deepcopy
from dataclasses import dataclass, field
from queue import PriorityQueue
from typing import Optional
import pygame

from ai_neural_net import NeuralNetGraph
from game_state import Actor, GameState
from helpers import grid_distance, within_grid
from vector import Vector

import ai_constants as ai_const
import game_constants as g_const
import game_controls


@dataclass(order=True)
class TileItem:
    priority: int
    distance: int
    tile: Vector = field(compare=False)


class AIController(game_controls.Controller):
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
        self.control_outputs(grid, directions)

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
        targets = [ghost.actor.tile() for ghost in self.game.ghosts() if ghost.state != 'inactive']

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
            score_distance = 1
            while grid[next_tile.y][next_tile.x] not in target_tiles:
                next_tile += direction
                score_distance += 1

            if grid[next_tile.y][next_tile.x] in g_const.BAD_TILES:
                out.append(ai_const.INACTIVE)
            else:
                out.append(1 / max(ai_const.ACTIVE, score_distance - ai_const.DOTS_BIAS))

            # Check the distances to ghosts in direction
            if targets != []:
                out.append(1 / self.a_star_distance(grid, targets, direction))
            else:
                out.append(ai_const.INACTIVE)

        # Check if all ghosts are frightened
        if all(ghost.get_frightened() for ghost in self.game.ghosts()):
            out.append(ai_const.ACTIVE)
        else:
            out.append(ai_const.INACTIVE)

        # Input bias node
        out.append(ai_const.ACTIVE)

    def a_star_distance(self, grid: list[list[int]], targets: list[Vector],
                        direction: Vector) -> int:
        path_grid = deepcopy(grid)
        tile_queue = PriorityQueue()
        tile = self.actor.tile()

        tile_queue.put(TileItem(0, 0, tile + direction))
        path_grid[tile.y][tile.x] = g_const.OUT

        while not tile_queue.empty():
            item = tile_queue.get()
            distance = item.distance + 1

            for candidate in g_const.DIRECTION.values():
                next_tile = item.tile + candidate

                if next_tile in targets:
                    return distance
                elif path_grid[next_tile.y][next_tile.x] not in g_const.BAD_TILES:
                    heuristic = self.distance_heuristic(next_tile, targets)
                    tile_queue.put(TileItem(heuristic + distance, distance, next_tile))

                    path_grid[next_tile.y][next_tile.x] = g_const.OUT

        return -1

    @staticmethod
    def distance_heuristic(position: Vector, targets: list[Vector]) -> int:
        return min(grid_distance(position, target) for target in targets)

    def control_outputs(self, grid: list[list[int]], directions: list[Vector]) -> None:
        net_int = [0, 1, 0, 0]

        dir_index = net_int.index(max(net_int))
        self.actor.change_direction(grid, directions[dir_index])

    def reset(self) -> None:
        self.last_score = (self.game.score, self.ticks_alive)

    def draw_debug(self, screen: pygame.Surface) -> None:
        pass


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['copy', 'queue', 'pygame', 'ai_constants', 'ai_neural_net',
                          'game_constants', 'game_controls', 'game_state', 'helpers', 'vector'],
        'max-line-length': 100,
        'disable': ['E1136']
    })

    import python_ta.contracts
    python_ta.contracts.DEBUG_CONTRACTS = True
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()
