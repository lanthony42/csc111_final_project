"""CSC111 Final Project

Module with containing the NeuralNetGraph class, which acts as the brain of the AI controller.
This module is based off the graph code from the Course Nodes and Assignment 3, though
heavily modified.
"""
from __future__ import annotations

from typing import Union
import csv
import random
import scipy.special

from helpers import clamp
import ai_constants as const


class _WeightedVertex:
    """A weighted vertex in the neural network.

    Instance Attributes:
        - number: The number of the vertex.
        - kind: The type of node within the neural network.
        - value: The node's outputted value.
        - neighbors: The node's neighbours as a dict mapping the neighbor vertex to edge weight

    Representation Invariants:
        - self.number >= 0
        - self.kind in {'input', 'hidden', 'output'}
    """
    number: int
    kind: str
    value: float

    neighbours: dict[_WeightedVertex, Union[int, float]]

    def __init__(self, number: int, kind: str) -> None:
        """Initialize a new vertex with the given number.

        Preconditions:
            - number >= 0
            - kind in {'input', 'hidden', 'output'}

        Args:
            - number: The number of the vertex.
            - kind: The type of node within the neural network.
        """
        self.number = number
        self.kind = kind
        self.value = 0

        self.neighbours = {}

    def get_connections(self) -> list[tuple[int, int, float]]:
        """Recursively returns a list of all connects of the node and its neighbors.
        Returns a list of tuples containing the initial node, the end node, and the weight of edge.

        This implementation is valid because the neural network is a directed acyclic graph,
        thus the base case is naturally the input nodes.
        """
        # Input nodes are the base case.
        if self.kind == 'input':
            return []

        out = []
        for node, weight in self.neighbours.items():
            # Represent connections as the initial node, the end node, and weight of edge.
            out.append((self.number, node.number, weight))
            # Recursively get connections.
            out.extend(node.get_connections())

        return out

    def get_neighbor_numbers(self) -> set[int]:
        """Returns the numbers of all the node's neighbors."""
        return set(neighbor.item for neighbor in self.neighbours)


class NeuralNetGraph:
    """A directed acyclic graph class representing a neural network.

    Instance Attributes:
        - input_nodes: A list of the input nodes of the neural network.
        - output_nodes: A list of the output nodes of the neural network.
        - fitness: The fitness of the neural network implementation.

    Representation Invariants:
        - self.fitness >= 0
    """
    input_nodes: list[_WeightedVertex]
    output_nodes: list[_WeightedVertex]
    fitness: float

    # Private Instance Attributes:
    #  - _vertices : A mapping of the node's number to the vertex itself
    _vertices: dict[int, _WeightedVertex]

    def __init__(self, input_size: int, output_size: int, hidden_size: int = 1) -> None:
        """Initialize a graph with given amount of each node types.

        Preconditions:
            - input_size >= 0
            - output_size >= 0
            - hidden_size >= 0

        Args:
            - input_size: The amount of input nodes.
            - output_size: The amount of output nodes.
            - hidden_size: The amount of hidden nodes.
        """
        self._vertices = {}

        self.input_nodes = []
        self.output_nodes = []
        self.fitness = 0

        # Add input nodes.
        for _ in range(input_size):
            self.add_input_node()

        # Add and connect the hidden nodes.
        hidden_nodes = []
        for i in range(hidden_size):
            hidden_nodes.append(self._vertices[self.add_hidden_node()])

            for input_node in self.input_nodes:
                hidden_nodes[i].neighbours[input_node] = random.uniform(-1, 1)

        # Add and connect the output nodes.
        for _ in range(output_size):
            vertex = self._vertices[self.add_output_node()]

            for hidden_node in hidden_nodes:
                vertex.neighbours[hidden_node] = random.uniform(-1, 1)

    def add_input_node(self) -> int:
        """Add an input node to this graph and return the number.

        The new input node is not adjacent to any other vertices.
        """
        num = len(self._vertices) + 1
        new_vertex = _WeightedVertex(num, 'input')

        self._vertices[num] = new_vertex
        self.input_nodes.append(new_vertex)

        return num

    def add_hidden_node(self) -> int:
        """Add a hidden node to this graph and return the number.

        The new hidden node is not adjacent to any other vertices.
        """
        num = len(self._vertices) + 1
        new_vertex = _WeightedVertex(num, 'hidden')
        self._vertices[num] = new_vertex

        return num

    def add_output_node(self) -> int:
        """Add an output node to this graph and return the number.

        The new output node is not adjacent to any other vertices.
        """
        num = len(self._vertices) + 1
        new_vertex = _WeightedVertex(num, 'output')

        self._vertices[num] = new_vertex
        self.output_nodes.append(new_vertex)

        return num

    def add_edge(self, number1: int, number2: int, weight: Union[int, float] = 1) -> None:
        """Add an edge between the two vertices with the given numbers in this graph,
        with the given weight. The edge will only be added from number1 to number2,
        creating a directed graph.

        Raise a ValueError if number1 or number2 do not appear as vertices in this graph.
        Thus, this aspect won't be included in preconditions.

        Preconditions:
            - number1 >= 0
            - number2 >= 0

        Args:
            - number1: The number for the starting vertex.
            - number2: The number for the ending vertex.
            - weight: The weight of the new edge.
        """
        if number1 in self._vertices and number2 in self._vertices:
            v1 = self._vertices[number1]
            v2 = self._vertices[number2]

            # Add the new directed edge
            v1.neighbours[v2] = weight
        else:
            # We didn't find an existing vertex for both items.
            raise ValueError

    def get_weight(self, number1: int, number2: int) -> Union[int, float]:
        """Return the weight of the edge between the given numbers, from number1 to number2.

        Return 0 if number1 and number2 are not adjacent.

        Preconditions:
            - number1 in self._vertices.keys()
            - number2 in self._vertices.keys()

        Args:
            - number1: The number for the starting vertex.
            - number2: The number for the ending vertex.
        """
        v1 = self._vertices[number1]
        v2 = self._vertices[number2]

        return v1.neighbours.get(v2, 0)

    def get_connections(self) -> list[tuple[int, int, float]]:
        """Return all the connections within the neural net.
        Returns a list of tuples containing the initial node, the end node, and the weight of edge.
        """
        out = []
        for node in self.output_nodes:
            out.extend(node.get_connections())

        return out

    def get_hidden_count(self) -> int:
        """Return the amount of hidden nodes in the neural net."""
        return len(self._vertices) - len(self.input_nodes) - len(self.output_nodes)

    def propagate_outputs(self) -> None:
        """The main function to update all values for the output nodes."""
        for node in self.output_nodes:
            self._propagate_node(node, set())

    def _propagate_node(self, curr_node: _WeightedVertex, visited: set()) -> None:
        """Updates the values of all nodes curr_node relies on, then updates its value.

        Is a recursive helper function for propagate_outputs, relying on the natural base case
        of the input nodes, given the neural network is a directed acyclic graph.

        Preconditions:
            - curr_node.number not in visited

        Args:
            - curr_node: The current node to be updated.
            - visited: The set of node numbers corresponding to already visited thus updated nodes.
        """
        # Input nodes as base case
        if curr_node.kind == 'input':
            return

        visited.add(curr_node.number)
        value = 0

        # Update all nodes curr_node relies on (The node's neighbors).
        for node, weight in curr_node.neighbours.items():
            if node.number not in visited:
                self._propagate_node(node, visited)
            value += node.value * weight

        # Sigmoid activation function!
        curr_node.value = scipy.special.expit(value)

    def get_mutated_child(self, best_fitness: float) -> NeuralNetGraph:
        """Returns a copy of the graph with slightly mutated edge weights.

        Preconditions:
            - best_fitness >= 0

        Args:
            - best_fitness: The best fitness for the training.
        """
        # Start making a copy of this neural network
        new_network = NeuralNetGraph(len(self.input_nodes), len(self.output_nodes),
                                     self.get_hidden_count())
        # Modification factor depends on best fitness - better fitness, more precise mutations.
        factor = 1 / (const.WEIGHT_CO - max(const.WEIGHT_OFFSET - best_fitness / const.FITNESS_CO,
                                            0))

        # Add all connections with mutations
        for v1, v2, weight in self.get_connections():
            if random.uniform(0, 1) < const.RANDOM_CHANCE:
                weight = random.uniform(-1, 1)
            else:
                weight = clamp(weight + factor * random.gauss(0, 1), -1, 1)
            new_network.add_edge(v1, v2, weight)

        return new_network


def load_neural_network(file_path: str) -> NeuralNetGraph:
    """Returns neural network from the csv file at file_path.

    Preconditions:
        - file_path is a valid path to a csv file.

    Args:
        - file_path: The path for a csv file storing the neural network representation.
    """
    with open(file_path) as csv_file:
        reader = csv.reader(csv_file)
        initial_sizes = next(reader)

        # First row of csv are the sizes of the node types.
        neural_net = NeuralNetGraph(int(initial_sizes[0]), int(initial_sizes[1]),
                                    int(initial_sizes[2]))

        # Add all the rows as edge connections.
        for connection in reader:
            neural_net.add_edge(int(connection[0]), int(connection[1]), float(connection[2]))

        return neural_net


def save_neural_network(neural_net: NeuralNetGraph, file_path: str) -> None:
    """Saves the neural network as a csv file.

    Preconditions:
        - file_path is a valid path for a csv file, which may or may not exist yet.

    Args:
        - neural_net: The neural network to be saved.
        - file_path: The path for a csv file storing the neural network representation.
    """
    with open(file_path, 'w+', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        # Output the sizes of the node types.
        connections = [(len(neural_net.input_nodes), len(neural_net.output_nodes),
                        neural_net.get_hidden_count())]

        # Write the connections.
        writer.writerows(connections + neural_net.get_connections())


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['csv', 'random', 'scipy.special', 'ai_constants', 'helpers'],
        'allowed-io': ['load_neural_network', 'save_neural_network'],
        'max-line-length': 100,
        'disable': ['E1136', 'E1101']
    })

    import python_ta.contracts
    python_ta.contracts.DEBUG_CONTRACTS = False
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()
