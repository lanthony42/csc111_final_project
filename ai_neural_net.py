from __future__ import annotations

from typing import Union
import csv
import scipy.special
from math import sqrt
from numpy import mean
from numpy.random import rand


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

    def degree(self) -> int:
        """Return the degree of this vertex."""
        return len(self.neighbours)


class NeuralNetGraph:
    """A graph representing a neural network.
    """
    _vertices: dict[int, _WeightedVertex]

    input_nodes: list[_WeightedVertex]
    output_nodes: list[_WeightedVertex]
    curr_num: int
    fitness: int

    def __init__(self, input_size: int, output_size: int) -> None:
        """Initialize an empty graph (no vertices or edges)."""
        self._vertices = {}

        self.input_nodes = []
        self.output_nodes = []
        self.curr_num = 0
        self.fitness = 0

        for _ in range(input_size):
            self.add_input_node()

        for _ in range(output_size):
            self.add_output_node()

    def add_input_node(self) -> int:
        """Add an input node with the given number to this graph.

        The new input node is not adjacent to any other vertices.
        """
        self.curr_num += 1
        new_vertex = _WeightedVertex(self.curr_num, 'input')

        self._vertices[self.curr_num] = new_vertex
        self.input_nodes.append(new_vertex)

        return self.curr_num

    def add_hidden_node(self) -> int:
        """Add a hidden node with the given item to this graph.

        The new hidden node is not adjacent to any other vertices.
        """
        self.curr_num += 1
        new_vertex = _WeightedVertex(self.curr_num, 'hidden')
        self._vertices[self.curr_num] = new_vertex

        return self.curr_num

    def add_output_node(self) -> int:
        """Add an output node with the given item to this graph.

        The new output node is not adjacent to any other vertices.
        """
        self.curr_num += 1
        new_vertex = _WeightedVertex(self.curr_num, 'output')

        self._vertices[self.curr_num] = new_vertex
        self.output_nodes.append(new_vertex)

        return self.curr_num

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


def load_neural_network(file_path: str) -> NeuralNetGraph:
    with open(file_path) as csv_file:
        reader = csv.reader(csv_file)

        initial_sizes = next(reader)
        connections = list(reader)

        input_size = int(initial_sizes[0])
        output_size = int(initial_sizes[1])
        neural_net = NeuralNetGraph(input_size, output_size)

        # Find and add all hidden layer nodes
        hidden_count = len(set(connect[0] for connect in connections
                               if int(connect[0]) > input_size + output_size))
        for _ in range(hidden_count):
            neural_net.add_hidden_node()

        for connection in connections:
            neural_net.add_edge(int(connection[0]), int(connection[1]), float(connection[2]))

        return neural_net


def save_neural_network(neural_net: NeuralNetGraph, file_path: str) -> None:
    with open(file_path, 'w+', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        connections = [(len(neural_net.input_nodes), len(neural_net.output_nodes))]

        writer.writerows(connections + neural_net.get_connections())


def create_neural_network(size_l: list[int]) -> tuple[NeuralNetGraph, list]:
    """Creates a graph for the neural network,
    size_l is a list containing the sizes of each layer"""
    new_graph = NeuralNetGraph(size_l[0], size_l[-1])
    layers = [[node.number for node in new_graph.input_nodes]]
    initial_num = size_l[0] + size_l[-1]

    for i in range(1, len(size_l) - 1):
        layers.append([num for num in range(initial_num + 1, initial_num + size_l[i] + 1)])
        initial_num = max(layers[-1])

    layers.append([node.number for node in new_graph.output_nodes])

    weights_list = []

    for i in range(1, len(size_l) - 1):
        n1 = size_l[i - 1]
        n2 = size_l[i]
        lower, upper = -(1.0 / sqrt(n1)), (1.0 / sqrt(n1))
        weights = rand(n2, n1)
        weights_list.append(weights)

        for num2 in range(0, n2):
            new_graph.add_hidden_node()
            for num1 in range(0, n1):
                new_graph.add_edge(layers[i][num2], layers[i - 1][num1], weights[num2][num1])

    n3 = size_l[-2]
    n4 = size_l[-1]
    lower, upper = -(1.0 / sqrt(n3)), (1.0 / sqrt(n3))
    weights = rand(n4, n3)
    weights_list.append(weights)

    for num4 in range(0, n4):
        for num3 in range(0, n3):
            new_graph.add_edge(layers[-1][num4], layers[-2][num3], weights[num4][num3])

    return (new_graph, weights_list[::-1])


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['csv', 'scipy.special'],
        'allowed-io': ['load_neural_network', 'save_neural_network'],
        'max-line-length': 100,
        'disable': ['E1136', 'E1101']
    })

    import python_ta.contracts
    python_ta.contracts.DEBUG_CONTRACTS = False
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()
