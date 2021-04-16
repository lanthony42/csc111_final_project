from __future__ import annotations

from typing import Union
import csv
import random
import scipy.special

from helpers import clamp
import ai_constants as const


class _WeightedVertex:
    """A vertex in a graph.
    """
    number: int
    kind: str
    value: float

    neighbours: dict[_WeightedVertex, Union[int, float]]

    def __init__(self, number: int, kind: str) -> None:
        """Initialize a new vertex with the given number.

        Preconditions:
            - number > 0
            - kind in {'input', 'hidden', 'output'}
        """
        self.number = number
        self.kind = kind
        self.value = 0

        self.neighbours = {}

    def get_connections(self) -> list[tuple[int, int, float]]:
        if self.kind == 'input':
            return []

        out = []
        for node, weight in self.neighbours.items():
            out.append((self.number, node.number, weight))
            out.extend(node.get_connections())

        return out

    def get_neighbor_numbers(self) -> set[int]:
        return set(neighbor.item for neighbor in self.neighbours)


class NeuralNetGraph:
    """A graph representing a neural network.
    """
    _vertices: dict[int, _WeightedVertex]

    input_nodes: list[_WeightedVertex]
    output_nodes: list[_WeightedVertex]
    fitness: int

    def __init__(self, input_size: int, output_size: int, hidden_size: int = 1) -> None:
        """Initialize a graph with given amount of each node types."""
        self._vertices = {}

        self.input_nodes = []
        self.output_nodes = []
        self.fitness = 0

        for _ in range(input_size):
            self.add_input_node()

        hidden_nodes = []
        for i in range(hidden_size):
            hidden_nodes.append(self._vertices[self.add_hidden_node()])

            for input_node in self.input_nodes:
                hidden_nodes[i].neighbours[input_node] = random.uniform(-1, 1)

        for _ in range(output_size):
            vertex = self._vertices[self.add_output_node()]

            for hidden_node in hidden_nodes:
                vertex.neighbours[hidden_node] = random.uniform(-1, 1)

    def add_input_node(self) -> int:
        """Add an input node with the given number to this graph.

        The new input node is not adjacent to any other vertices.
        """
        num = len(self._vertices) + 1
        new_vertex = _WeightedVertex(num, 'input')

        self._vertices[num] = new_vertex
        self.input_nodes.append(new_vertex)

        return num

    def add_hidden_node(self) -> int:
        """Add a hidden node with the given item to this graph.

        The new hidden node is not adjacent to any other vertices.
        """
        num = len(self._vertices) + 1
        new_vertex = _WeightedVertex(num, 'hidden')
        self._vertices[num] = new_vertex

        return num

    def add_output_node(self) -> int:
        """Add an output node with the given item to this graph.

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
        """
        v1 = self._vertices[number1]
        v2 = self._vertices[number2]

        return v1.neighbours.get(v2, 0)

    def get_connections(self) -> list[tuple[int, int, float]]:
        out = []
        for node in self.output_nodes:
            out.extend(node.get_connections())

        return out

    def get_hidden_count(self) -> int:
        return len(self._vertices) - len(self.input_nodes) - len(self.output_nodes)

    def propagate_outputs(self) -> None:
        for node in self.output_nodes:
            self._propagate_node(node, set())

    def _propagate_node(self, curr_node: _WeightedVertex, visited: set()) -> None:
        if curr_node.kind == 'input':
            return

        visited.add(curr_node.number)
        value = 0

        for node, weight in curr_node.neighbours.items():
            if node.number not in visited:
                self._propagate_node(node, visited)
            value += node.value * weight

        curr_node.value = scipy.special.expit(value)

    def get_mutated_child(self, best_fitness: float) -> NeuralNetGraph:
        new_network = NeuralNetGraph(len(self.input_nodes), len(self.output_nodes),
                                     self.get_hidden_count())
        factor = 1 / (const.WEIGHT_CO - max(0, const.WEIGHT_OFFSET - \
                                            best_fitness / const.FITNESS_CO))

        for v1, v2, weight in self.get_connections():
            if random.uniform(0, 1) < const.RANDOM_CHANCE:
                weight = random.uniform(-1, 1)
            else:
                weight = clamp(weight + factor * random.gauss(0, 1), -1, 1)
            new_network.add_edge(v1, v2, weight)

        return new_network


def load_neural_network(file_path: str) -> NeuralNetGraph:
    with open(file_path) as csv_file:
        reader = csv.reader(csv_file)
        initial_sizes = next(reader)

        neural_net = NeuralNetGraph(int(initial_sizes[0]), int(initial_sizes[1]),
                                    int(initial_sizes[2]))
        for connection in reader:
            neural_net.add_edge(int(connection[0]), int(connection[1]), float(connection[2]))

        return neural_net


def save_neural_network(neural_net: NeuralNetGraph, file_path: str) -> None:
    with open(file_path, 'w+', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        connections = [(len(neural_net.input_nodes), len(neural_net.output_nodes),
                        neural_net.get_hidden_count())]

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
