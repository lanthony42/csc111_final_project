"""CSC111 Final Project

Module with containing the AITree and AITrainer classes for training of the AIs.
"""
from __future__ import annotations

from typing import Any, Optional
from os.path import isfile
import atexit
import math
import random

from ai_controls import AIController
from ai_neural_net import NeuralNetGraph, load_neural_network, save_neural_network
import ai_constants as const
import game_runner


class AITree:
    """A tree class representing the AIs simulated.

    Instance Attributes:
        - neural_net: The neural net corresponding to this tree's root value.
        - best_descendant: The best neural network from this tree's root value or descendants.
        - total_fitness: The total fitness of this tree's root value and descendants.
        - descendant_count: The amount of descendants for this tree.
        - enabled: Whether this tree is active.

    Representation Invariants:
        - self.total_fitness >= 0
        - self.descendant_count >= 0

        - self.descendant_count, self.total_fitness, self.best_descendant match with their
          descriptions relative to the root value and descendants of this tree
    """
    neural_net: NeuralNetGraph
    best_descendant: NeuralNetGraph
    total_fitness: float
    descendant_count: int
    enabled: bool

    # Private Instance Attributes:
    #  - _parent : The parent of this tree. If equal to None, this indicates this is the overall
    #              root.
    #  - _subtrees : The list of this tree's subtrees.
    _parent: Optional[AITree]
    _subtrees: list[AITree]

    def __init__(self, neural_net: NeuralNetGraph) -> None:
        """Makes new AI Tree from neural network assuming simulation has already ran on network.

        Args:
            - neural_net: The neural network which is this tree's root value.
        """
        self.neural_net = neural_net
        self.best_descendant = neural_net
        self.total_fitness = neural_net.fitness
        self.descendant_count = 0
        self.enabled = True

        self._parent = None
        self._subtrees = []

    def get_subtrees(self) -> list[AITree]:
        """Returns all this tree's subtrees"""
        return self._subtrees

    def set_parent(self, parent: AITree) -> None:
        """Sets this tree's parent tree.

        Preconditions:
            - self in parent.get_subtrees()

        Args:
            - parent: The tree to be set as this tree's parent
        """
        self._parent = parent

    def is_leaf(self) -> bool:
        """Returns whether or not this tree is a leaf."""
        return self._subtrees == []

    def add_subtree(self, neural_net: NeuralNetGraph) -> None:
        """Adds a neural network to this tree as a subtree, then updates information to maintain
        the representation invariants.

        Args:
            - neural_net: The neural network to be added.
        """
        subtree = AITree(neural_net)
        self._subtrees.append(subtree)
        subtree.set_parent(self)

        # Recursively updates fitness values
        self.recurse_update_fitness(subtree)

    def recurse_update_fitness(self, subtree: AITree) -> None:
        """Updates fitness after given subtree is added, then recurses into parent tree, thus
        maintaining representation invariants.

        Preconditions:
            - subtree in self.get_subtrees()

        Args:
            - subtree: The subtree from which this method was called.
        """
        self.total_fitness += subtree.total_fitness
        self.descendant_count += 1

        # Replace best_descendant if the subtree's was better
        if subtree.best_descendant.fitness > self.best_descendant.fitness:
            self.best_descendant = subtree.best_descendant

        # Continue to recurse until root of overall tree
        if self._parent is not None:
            self._parent.recurse_update_fitness(subtree)

    def choose_next_parent(self) -> AITree:
        """Returns the next parent using a Monte Carlo Tree Search type algorithm."""
        if self.is_leaf():
            return self
        else:
            # Expansion by adding new subtree
            if random.uniform(0, 1) < const.EXPANSION_CHANCE / len(self._subtrees):
                return self
            else:
                # Chooses best tree based on heuristic,then recurses to find the best tree
                # to return.
                max_tree = max(self._subtrees, key=self.exploration_heuristic)
                return max_tree.choose_next_parent()

    def exploration_heuristic(self, subtree: AITree) -> float:
        """Returns heuristic value of given subtree, using formula based on commonly used
        Monte Carlo Tree Search formula.

        Args:
            - subtree: The subtree to calculate heuristic value of.
        """
        # Will only choose disabled subtree if no other available nodes.
        if not subtree.enabled:
            return 0
        elif subtree.descendant_count == 0:
            return math.inf

        exploitation_term = subtree.total_fitness / subtree.descendant_count
        exploration_term = math.sqrt(math.log(self.descendant_count) / subtree.descendant_count)

        return exploitation_term + const.EXPLORATION_CO * exploration_term

    def extinction(self) -> None:
        """Causes extinction event in which the lowest average fitness and best fitness trees
        get deactivated. If the subtree has poor average fitness but not poor best fitness, the
        extinction will recurse into the subtree to preserve best fitness.
        """
        if self.descendant_count < const.EXTINCTION_MIN:
            return

        # Find subtrees with worst best fitness and worst average fitness.
        amount = len(self._subtrees) // const.EXTINCTION_AMOUNT
        by_best = sorted(self._subtrees, key=lambda x: x.best_descendant.fitness)[:amount]
        by_avg = sorted(self._subtrees,
                        key=lambda x: x.total_fitness / max(1, x.descendant_count))[:amount]

        # Disable the trees that appear in both lists.
        for subtree in by_best:
            if subtree in by_avg:
                subtree.enabled = False
                by_avg.remove(subtree)

        # If only appears in worst average fitness list, recursively call extinction
        for subtree in by_avg:
            subtree.extinction()


class AITrainer:
    """A class used to train the AIs using the AI tree system.

    Instance Attributes:
        - ai_tree: The AI tree to be used to choose neural network to mutate from.
        - best_fitness: The tuple of best average fitness and time of this best fitness.
        - rolling_avg: The list of fitness used in rolling average calculation.
        - game: The game used to simulate the results.
        - training_stage: The stage of training the trainer is on.
        - has_won: Whether there has been a winning instance.

    Representation Invariants:
        - self.best_fitness[0] >= 0 and self.best_fitness[1] >= 0
        - len(self.rolling_avg) <= const.ROLLING_AVG_COUNT
        - 0 <= self.training_stage <= 3
    """
    ai_tree: AITree
    best_fitness: tuple[float, int]
    rolling_avg: list[float]
    game: game_runner.Game
    training_stage: int
    has_won: bool

    def __init__(self) -> None:
        """Initializes a trainer object."""
        self.ai_tree = None
        self.best_fitness = (0.0, 0)
        self.rolling_avg = []
        self.game = game_runner.Game('data/map.csv')

        self.training_stage = const.TRAVERSAL_STAGE
        self.has_won = False

    def start_training(self, input_path: Optional[str] = None, output_path: Optional[str] = None,
                       starting_stage: int = const.GHOST_STAGE, is_visual: bool = False) -> None:
        """Starts the training of AI at given stage. Takes initial neural network from input_path,
        and outputs to output_path. May be done with visualization.

        Args:
            - input_path: The path for the initial neural network saved as a csv file.
            - output_path: The path for the output of the training to go, as a csv file.
            - starting_stage: The stage to start training from.
            - is_visual: Whether or not to show visualizations.
        """
        # Reset values for each training
        self.training_stage = starting_stage
        self.best_fitness = (0.0, 0)
        self.rolling_avg = []
        self.has_won = False

        # Initialize AI Tree
        if input_path is not None and isfile(input_path):
            initial_net = load_neural_network(input_path)
        else:
            initial_net = NeuralNetGraph(const.INPUT_SIZE, const.OUTPUT_SIZE, const.HIDDEN_SIZE)
        self.ai_tree = AITree(initial_net)

        # Remember to save on exit!
        atexit.register(self.on_exit, output_path)

        iteration = 0
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

            # Selection and Expansion step for iteration
            parent = self.ai_tree.choose_next_parent()
            neural_net = parent.neural_net.get_mutated_child(self.ai_tree.best_descendant.fitness)

            # Start simulation step for iteration
            if self.simulate(neural_net, config):
                break
            # Backpropagation step for iteration
            parent.add_subtree(neural_net)
            self.rolling_avg.append(neural_net.fitness)

            # Update rolling average
            if len(self.rolling_avg) > const.ROLLING_AVG_COUNT:
                self.rolling_avg.pop(0)

            # Check if there has been a staggering, then extinction
            if self.rolling_average() > self.best_fitness[0]:
                self.best_fitness = (self.rolling_average(), iteration)
            elif iteration - self.best_fitness[1] > const.STALENESS_THRESHOLD:
                self.ai_tree.extinction()
                self.best_fitness = (self.rolling_average(), iteration)
            iteration += 1

        self.on_exit(output_path)

    def rolling_average(self) -> float:
        """Returns a rolling average of the recent neural networks' fitness."""
        if len(self.rolling_avg) > 0:
            return sum(self.rolling_avg) / len(self.rolling_avg)
        else:
            return 0.0

    def on_exit(self, graph_path: Optional[str] = None) -> None:
        """Saves the outcomes of training into file at graph_path.

        Args:
            - graph_path: The path for the output of the training to go, as a csv file.
        """
        if graph_path is not None:
            save_neural_network(self.ai_tree.best_descendant, graph_path)
            print('Saved!')

    def simulate(self, network: NeuralNetGraph, config: Optional[dict[str, Any]] = None) -> bool:
        """Simulates a game with given neural network and returns if has force quit.

        Args:
            - network: The neural network to simulate.
            - config: The configuration dictionary for simulations.
        """
        outcome = self.game.run(player_controller=AIController, neural_net=network, config=config)

        if outcome.pop('force_quit'):
            return True

        if self.training_stage < len(const.SCORE_THRESHOLD) and \
                outcome['score'] >= const.SCORE_THRESHOLD[self.training_stage]:
            self.training_stage += 1

        self.has_won = outcome['game_win'] and self.training_stage >= const.BOOST_STAGE
        network.fitness = self.fitness(**outcome)

        if not config['is_visual']:
            self.non_visual_output(outcome, network.fitness)

        return False

    def non_visual_output(self, outcome: dict[str, Any], fitness: int) -> None:
        """Outputs useful information in console for non-visual training.

        Args:
            - outcome: The outcome of current iteration's simulation.
            - fitness: The current iteration's neural network's fitness.
        """
        print('Average Fitness', self.rolling_average())
        print('Best Fitness:', self.ai_tree.best_descendant.fitness)
        print('Training Stage:', self.training_stage)

        print('Has Won:', outcome['game_win'], 'Score:', outcome['score'], 'Time Alive:',
              outcome['time_alive'])
        print('Simulation Fitness:', fitness)

    @staticmethod
    def fitness(game_win: bool, score: int, time_alive: int) -> float:
        """Returns the fitness score of the given simulation game.

        Args:
            - game_win: Whether the game was won.
            - score: The score of the game.
            - time_alive: The time in second-equivalents for which the player was alive.
        """
        return const.WIN_WEIGHT * int(game_win) + const.SCORE_WEIGHT * score + \
            const.TIME_WEIGHT * time_alive


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['atexit', 'math', 'os.path', 'random', 'ai_constants', 'ai_controls',
                          'ai_neural_net', 'game_runner'],
        'allowed-io': ['on_exit', 'non_visual_output'],
        'max-line-length': 100,
        'disable': ['E1136', 'E1101', 'E1123']  # PyTa doesn't recognize popping of 'force_quit'
    })

    import python_ta.contracts
    python_ta.contracts.DEBUG_CONTRACTS = False
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()
