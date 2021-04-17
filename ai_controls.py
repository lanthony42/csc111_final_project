"""CSC111 Final Project

Module with containing the AIController class, which controls the player using a neural network.
"""
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
    """A dataclass representing a tile for a PriorityQueue to sort. Note that this allows for
    the tile to not be sorted as part of the sorting.

    Instance Attributes:
        - priority: The priority of this tile.
        - distance: The current distance traveled to this tile.
        - tile: The tile's position on the grid.
    """
    priority: int
    distance: int
    tile: Vector = field(compare=False)


class AIController(game_controls.Controller):
    """A class representing a controller which uses a neural network to control an actor.

    Instance Attributes:
        - neural_net: The neural network associated with the controller.
        - ticks_alive: The amount of ticks the player has survived for.
        - last_score: A tuple containing the last score and the tick where this was achieved.

    Representation Invariants:
        - self.ticks_alive >= 0
        - self.last_score[0] >= 0 and self.last_score[1] >= 0
    """
    neural_net: Optional[NeuralNetGraph]
    ticks_alive: int
    last_score: tuple[int, int]

    def __init__(self, game: GameState, actor: Actor,
                 neural_net: Optional[NeuralNetGraph] = None) -> None:
        """Initialize an AI controller object.

        Args:
            - game: The current game's game state object.
            - actor: The associated actor object.
            - neural_net: The associated neural network object.
        """
        super().__init__(game, actor)
        self.neural_net = neural_net

        self.ticks_alive = 0
        self.last_score = (0, self.ticks_alive)

    def control(self, grid: list[list[int]]) -> None:
        """Controls the player using the neural network.

        Args:
            - grid: The current game's map grid.
        """
        directions = list(ai_const.DIRECTION_ROTATE)

        # Create a list of directions around the player's current direction
        direct = self.actor.state.direction
        if direct not in directions:
            dir_index = 0
        else:
            dir_index = directions.index(direct)

        end_index = dir_index + len(directions) // 2
        directions = directions[dir_index: end_index]

        # Propagate through neural network
        if self.is_check_neural_net(grid, directions):
            self.get_inputs(grid, directions)
            self.neural_net.propagate_outputs()
            self.control_outputs(grid, directions)

        # Checks if player has been inactive
        self.ticks_alive += 1
        timeout = (ai_const.POINT_TIMEOUT - max(0, (ai_const.POINT_OFFSET - self.game.score) // 10))

        if self.game.score != self.last_score[0]:
            self.last_score = (self.game.score, self.ticks_alive)
        elif self.ticks_alive - self.last_score[1] > timeout:
            self.game.lives = 0

    def is_check_neural_net(self, grid: list[list[int]], directions: list[Vector]) -> bool:
        """Returns whether or not the neural network should be checked, depending on if player
        can turn left or right.

        Args:
            - grid: The current game's map grid.
            - directions: The list of directions around the player's current direction.
        """
        tile = self.actor.tile()
        left_tile = tile + directions[1]
        right_tile = tile + directions[-1]

        can_left = grid[left_tile.y][left_tile.x] not in g_const.BAD_TILES
        can_right = grid[right_tile.y][right_tile.x] not in g_const.BAD_TILES

        return can_left or can_right

    def get_inputs(self, grid: list[list[int]], directions: list[Vector]) -> None:
        """Updates the neural network's input nodes.

        Args:
            - grid: The current game's map grid.
            - directions: The list of directions around the player's current direction.
        """
        inputs = []
        tile = self.actor.tile()
        # Targets to be searched for
        target_tiles = {g_const.WALL, g_const.DOOR, g_const.OUT, g_const.DOT, g_const.BOOST}
        # Get ghost positions
        targets = [ghost.actor.tile() for ghost in self.game.ghosts() if ghost.state != 'inactive']

        # Get inputs for every direction around the player
        for direction in directions:
            next_tile = tile + direction

            # Check if can move in this direction
            if not within_grid(next_tile) or grid[next_tile.y][next_tile.x] in g_const.BAD_TILES:
                inputs.append(ai_const.ACTIVE)
            else:
                inputs.append(ai_const.INACTIVE)

            # Check if score can be increased in this direction
            score_distance = 1
            while grid[next_tile.y][next_tile.x] not in target_tiles:
                next_tile += direction
                score_distance += 1

            if grid[next_tile.y][next_tile.x] in g_const.BAD_TILES:
                inputs.append(ai_const.INACTIVE)
            else:
                inputs.append(1 / max(ai_const.ACTIVE, score_distance - ai_const.DOTS_BIAS))

            # Check the distances to ghosts in direction
            if targets != []:
                distance = self.a_star_distance(grid, targets, direction)
                inputs.append(max(ai_const.INACTIVE, 1 / distance))
            else:
                inputs.append(ai_const.INACTIVE)

        # Check if all ghosts are frightened
        if all(ghost.get_frightened() for ghost in self.game.ghosts()):
            inputs.append(ai_const.ACTIVE)
        else:
            inputs.append(ai_const.INACTIVE)

        # Input bias node
        inputs.append(ai_const.ACTIVE)

        # Place input into input nodes
        for node, value in zip(self.neural_net.input_nodes, inputs[:ai_const.INPUT_SIZE]):
            node.value = value

    def a_star_distance(self, grid: list[list[int]], targets: list[Vector],
                        direction: Vector) -> int:
        """By treating the grid as a representation of a graph, A Star is used to return shortest
        distance needed to travel to get to a target position in direction.

        Args:
            - grid: The current game's map grid which is used like a graph.
            - targets: The target tiles to look for.
            - direction: The direction to check distance for.
        """
        # Sets up priority queue and copy of grid to track visited nodes.
        path_grid = deepcopy(grid)
        tile_queue = PriorityQueue()

        tile = self.actor.tile()
        # Don't allow revisiting of initial tile.
        path_grid[tile.y][tile.x] = g_const.OUT

        # Only append to queue if next direction isn't a bad tile
        next_tile = tile + direction
        if path_grid[next_tile.y][next_tile.x] not in g_const.BAD_TILES:
            tile_queue.put(TileItem(0, 0, next_tile))

        # Loop through until queue empty or target found.
        while not tile_queue.empty():
            item = tile_queue.get()
            distance = item.distance + 1

            # Check to see if each direction can be added.
            for candidate in g_const.DIRECTION.values():
                next_tile = item.tile + candidate

                if next_tile in targets:
                    # Target found!
                    return distance
                elif path_grid[next_tile.y][next_tile.x] not in g_const.BAD_TILES:
                    # Use heuristic function as part of the given tile's priority.
                    heuristic = self.distance_heuristic(next_tile, targets)
                    tile_queue.put(TileItem(heuristic + distance, distance, next_tile))

                    path_grid[next_tile.y][next_tile.x] = g_const.OUT

        # If no path found.
        return -1

    @staticmethod
    def distance_heuristic(position: Vector, targets: list[Vector]) -> int:
        """Underestimates the real distance by returning the smallest grid distance to a target.

        Args:
            - position: Starting position for distance.
            - targets: A list of target vectors as endpoints for distance.
        """
        return min(grid_distance(position, target) for target in targets)

    def control_outputs(self, grid: list[list[int]], directions: list[Vector]) -> None:
        """Taking the neural network's output nodes, move in an according direction.

        Args:
            - grid: The current game's map grid.
            - directions: The list of directions around the player's current direction.
        """
        net_int = [node.value for node in self.neural_net.output_nodes][:ai_const.OUTPUT_SIZE]
        max_value = max(net_int)

        if max_value >= ai_const.MOVE_THRESHOLD:
            dir_index = net_int.index(max_value)
            self.actor.change_direction(grid, directions[dir_index + 1])

    def reset(self) -> None:
        """Resets the last score value for when associated actor dies."""
        self.last_score = (self.game.score, self.ticks_alive)

    def draw_debug(self, screen: pygame.Surface) -> None:
        """Draws out debugging information. Not needed for this controller!

        Args:
            - screen: The pygame game screen.
        """


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['copy', 'queue', 'pygame', 'ai_constants', 'ai_neural_net',
                          'game_constants', 'game_controls', 'game_state', 'helpers', 'vector'],
        'max-line-length': 100,
        'disable': ['E1136']
    })

    import python_ta.contracts
    python_ta.contracts.DEBUG_CONTRACTS = False
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()
