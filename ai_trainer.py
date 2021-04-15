from __future__ import annotations

from typing import Any, Optional
import pygame

from ai_controls import AIController
from ai_neural_net import NeuralNetGraph
import ai_constants as ai_const
import game_runner


class AITree:
    neural_net: NeuralNetGraph
    change_from_parent: Optional[set[str]]
    is_active: bool
    fitness: int

    _subtrees: list[AITree]

    def __init__(self, neural_net: NeuralNetGraph, change_from_parent: Optional[set[str]] = None,
                 is_active: bool = True) -> None:
        self.neural_net = neural_net
        self.change_from_parent = change_from_parent
        self.is_active = is_active
        self.fitness = 0

        self._subtrees = []

    def get_subtrees(self) -> list[AITree]:
        return self._subtrees

    def add_subtree(self, subtree: AITree) -> None:
        self._subtrees.append(subtree)


class AITrainer:
    size: int
    generation: int
    game: game_runner.Game

    def __init__(self, size: int) -> None:
        self.size = size
        self.generation = 0
        self.game = game_runner.Game('data/map.csv')

    def start_training(self, is_visual: bool = False) -> None:
        has_won = False
        training_stage = ai_const.TRAVERSAL_STAGE

        while not has_won:
            config = {'is_visual': is_visual}
            if training_stage == ai_const.TRAVERSAL_STAGE:
                config['has_ghosts'] = False
                config['has_boosts'] = False
                config['lives'] = 1
            elif training_stage == ai_const.GHOST_STAGE:
                config['has_boosts'] = False
                config['lives'] = 1

            self.divide_to_groups()
            if self.simulate(config):
                break
            self.natural_selection()
            self.make_next_generation()

            self.generation += 1

        pygame.display.quit()
        pygame.quit()

    def divide_to_groups(self) -> None:
        pass

    def simulate(self, config: dict[str, Any]) -> bool:
        outcome = self.game.run(player_controller=AIController, config=config)
        if outcome.pop('force_quit'):
            return True

        fitness = self.fitness(**outcome)
        print(fitness)

        return False

    @staticmethod
    def fitness(game_win: bool, score: int, time_alive: int) -> float:
        return ai_const.WIN_WEIGHT * int(game_win) + ai_const.SCORE_WEIGHT * score + \
            ai_const.TIME_WEIGHT * time_alive

    def natural_selection(self) -> None:
        pass

    def make_next_generation(self) -> None:
        pass


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['pygame', 'ai_constants', 'ai_controls', 'ai_neural_net', 'game_runner'],
        'max-line-length': 100,
        'disable': ['E1136', 'E1101', 'E1123']  # PyTa doesn't recognize popping of 'force_quit'
    })

    import python_ta.contracts
    python_ta.contracts.DEBUG_CONTRACTS = True
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()
