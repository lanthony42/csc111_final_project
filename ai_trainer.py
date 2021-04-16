from __future__ import annotations

from typing import Any, Optional
from os.path import isfile
import math
import random
import pygame

from ai_controls import AIController
from ai_neural_net import NeuralNetGraph, load_neural_network, save_neural_network
import ai_constants as const
import game_runner


class AITree:
    neural_net: NeuralNetGraph
    best_descendant: NeuralNetGraph
    total_fitness: float
    descendant_count: int

    _parent: AITree
    _subtrees: list[AITree]

    def __init__(self, neural_net: NeuralNetGraph) -> None:
        """Makes new AI Tree from neural network assuming simulation has already ran on network.
        """
        self.neural_net = neural_net
        self.best_descendant = neural_net
        self.total_fitness = neural_net.fitness
        self.descendant_count = 0

        self._parent = None
        self._subtrees = []

    def get_subtrees(self) -> list[AITree]:
        return self._subtrees

    def set_parent(self, parent: AITree) -> None:
        self._parent = parent

    def is_leaf(self) -> bool:
        return self._subtrees == []

    def add_subtree(self, neural_net: NeuralNetGraph) -> None:
        subtree = AITree(neural_net)
        self._subtrees.append(subtree)
        subtree.set_parent(self)

        self.recurse_update_fitness(subtree)

    def recurse_update_fitness(self, subtree: AITree) -> None:
        self.total_fitness += subtree.total_fitness
        self.descendant_count += 1

        if subtree.best_descendant.fitness > self.best_descendant.fitness:
            self.best_descendant = subtree.best_descendant

        if self._parent is not None:
            self._parent.recurse_update_fitness(subtree)

    def choose_next_parent(self) -> AITree:
        if self.is_leaf():
            return self
        else:
            if random.uniform(0, 1) < const.EXPANSION_CHANCE / len(self._subtrees):
                return self
            else:
                max_tree = max(self._subtrees, key=self.exploration_heuristic)
                return max_tree.choose_next_parent()

    def exploration_heuristic(self, subtree: AITree) -> float:
        if subtree.descendant_count == 0:
            return math.inf

        exploitation_term = subtree.total_fitness / subtree.descendant_count
        exploration_term = math.sqrt(math.log(self.descendant_count) / subtree.descendant_count)

        return exploitation_term + const.EXPLORATION_CO * exploration_term


class AITrainer:
    ai_tree: AITree
    game: game_runner.Game
    training_stage: int
    has_won: bool

    def __init__(self) -> None:
        self.ai_tree = None
        self.game = game_runner.Game('data/map.csv')

        self.training_stage = const.TRAVERSAL_STAGE
        self.has_won = False

    def start_training(self, graph_path: Optional[str] = None, is_visual: bool = False) -> None:
        self.training_stage = const.TRAVERSAL_STAGE
        self.has_won = False

        # Initialize AI Tree
        if graph_path is None:
            initial_net = NeuralNetGraph(const.INPUT_SIZE, const.OUTPUT_SIZE, const.HIDDEN_SIZE)
        elif isfile(graph_path):
            print('ok')
            initial_net = load_neural_network(graph_path)
        else:
            initial_net = NeuralNetGraph(const.INPUT_SIZE, const.OUTPUT_SIZE, const.HIDDEN_SIZE)
        self.ai_tree = AITree(initial_net)

        while not self.has_won:
            # Configure training stage
            config = {'is_visual': is_visual}
            if self.training_stage == const.TRAVERSAL_STAGE:
                config['has_ghosts'] = False
                config['has_boosts'] = False
                config['lives'] = 1
            elif self.training_stage == const.GHOST_STAGE:
                config['has_boosts'] = False
                config['lives'] = 1
            elif self.training_stage == const.BOOST_STAGE:
                config['lives'] = 1
            print(len(self.ai_tree.get_subtrees()))
            print(self.training_stage)

            # Start simulation step for iteration
            parent = self.ai_tree.choose_next_parent()
            neural_net = parent.neural_net.get_mutated_child(self.ai_tree.best_descendant.fitness)

            if self.simulate(neural_net, config):
                break
            parent.add_subtree(neural_net)

            if self.ai_tree.best_descendant.fitness > 1600 and \
                    self.training_stage > const.GHOST_STAGE:
                break

        if graph_path is not None:
            save_neural_network(self.ai_tree.best_descendant, graph_path)

        pygame.display.quit()
        pygame.quit()

    def simulate(self, network: NeuralNetGraph, config: Optional[dict[str, Any]] = None) -> bool:
        outcome = self.game.run(player_controller=AIController, neural_net=network, config=config)

        if outcome.pop('force_quit'):
            return True

        if self.training_stage < len(const.SCORE_THRESHOLD) and \
                outcome['score'] >= const.SCORE_THRESHOLD[self.training_stage]:
            self.training_stage += 1

        self.has_won = self.has_won or outcome['game_win']
        network.fitness = self.fitness(**outcome)
        print(network.fitness)
        print(outcome)

        return False

    @staticmethod
    def fitness(game_win: bool, score: int, time_alive: int) -> float:
        return const.WIN_WEIGHT * int(game_win) + const.SCORE_WEIGHT * score + \
            const.TIME_WEIGHT * time_alive


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['math', 'os.path', 'random', 'pygame', 'ai_constants', 'ai_controls',
                          'ai_neural_net', 'game_runner'],
        'max-line-length': 100,
        'disable': ['E1136', 'E1101', 'E1123']  # PyTa doesn't recognize popping of 'force_quit'
    })

    import python_ta.contracts
    python_ta.contracts.DEBUG_CONTRACTS = True
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()
