"""NeuralNetGraph"""
from __future__ import annotations
from typing import Any
import numpy as np
import scipy.special


class _WeightedVertex:
    """A vertex in a graph.
    """
    item: Any
    neighbours: dict[_WeightedVertex, Union[int, float]]

    def __init__(self, item: Any) -> None:
        """Initialize a new vertex with the given item.

        This vertex is initialized with no neighbours.

        Preconditions:
            - kind in {'user', 'book'}
        """
        self.item = item
        self.neighbours = {}

    def degree(self) -> int:
        """Return the degree of this vertex."""
        return len(self.neighbours)

class InputNode(_WeightedVertex):
    pass

class HiddenNode(_WeightedVertex):
    pass

class OutputNode(_WeightedVertex):
    pass

class NeuralNetGraph:
    """A graph representing a neural network.
    """
    _vertices: dict[Any, Any]
    input_nodes: dict[Any, InputNode]
    hidden_nodes: dict[Any, HiddenNode]
    output_nodes: dict[Any, OutputNode]

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges)."""
        self._vertices = {}
        self.input_nodes = {}
        self.hidden_nodes = {}
        self.output_nodes = {}

    def add_input_node(self, item: Any) -> None:
        """Add an input node with the given item to this graph.

        The new input node is not adjacent to any other vertices.
        """
        new_vertex = InputNode(item)
        self._vertices[item] = new_vertex
        self.input_nodes[item] = new_vertex

    def add_hidden_node(self, item: Any) -> None:
        """Add a hidden node with the given item to this graph.

        The new hidden node is not adjacent to any other vertices.
        """
        new_vertex = HiddenNode(item)
        self._vertices[item] = new_vertex
        self.hidden_nodes[item] = new_vertex

    def add_output_node(self, item: Any) -> None:
        """Add an output node with the given item to this graph.

        The new output node is not adjacent to any other vertices.
        """
        new_vertex = OutputNode(item)
        self._vertices[item] = new_vertex
        self.output_nodes[item] = new_vertex

    def add_edge(self, item1: Any, item2: Any, weight: Union[int, float] = 1) -> None:
        """Add an edge between the two vertices with the given items in this graph,
        with the given weight.

        Raise a ValueError if item1 or item2 do not appear as vertices in this graph.
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]

            # Add the new edge
            v1.neighbours[v2] = weight
            v2.neighbours[v1] = weight
        else:
            # We didn't find an existing vertex for both items.
            raise ValueError

    def get_weight(self, item1: Any, item2: Any) -> Union[int, float]:
        """Return the weight of the edge between the given items.

        Return 0 if item1 and item2 are not adjacent.
        """
        v1 = self._vertices[item1]
        v2 = self._vertices[item2]
        return v1.neighbours.get(v2, 0)


def create_neural_network(inputs: List[Union[int, float]], num_hidden_nodes: int, num_output_nodes) -> NeuralNetGraph:
    """Creates a graph for the neural network with the given inputs."""
    new_graph = NeuralNetGraph()

    for input in inputs:
        new_graph.add_input_node(input)

    breakpoint()
    inputs_m = np.array(inputs, ndmin=2).T
    w1 = (np.random.randn(len(inputs), num_hidden_nodes) * np.sqrt(2 / num_hidden_nodes)).T
    hidden_input_1 = np.dot(w1, inputs_m)
    activation_function = lambda x: scipy.special.expit(x)
    hidden_output_1 = activation_function(hidden_input_1)

    for hidden_node in range(0, num_hidden_nodes):
        new_graph.add_hidden_node(hidden_output_1[hidden_node][0])
        for num in range(0, len(inputs)):
            new_graph.add_edge(inputs[num], hidden_output_1[hidden_node][0], w1[hidden_node][num])

    w2 = (np.random.randn(num_hidden_nodes, num_output_nodes) * np.sqrt(2 / num_output_nodes)).T
    hidden_input_2 = np.dot(w2, hidden_output_1)
    hidden_output_2 = activation_function(hidden_input_2)

    for output_node in range(0, num_output_nodes):
        new_graph.add_hidden_node(hidden_output_2[output_node][0])
        for hidden_node in range(0, num_hidden_nodes):
            new_graph.add_edge(hidden_output_1[hidden_node][0], hidden_output_2[output_node][0], w2[output_node][hidden_node])

    return NeuralNetGraph

def create_neural_network2(inputs: List[Union[int, float]], l: int, size_l: List[int], size_o: int) -> None:
    """Creates a graph for the neural network with the given inputs. l denotes number of hidden layers,
    size_l is a list containing the sizes of each hidden layer, and size_o is the number of outputs"""
    new_graph = NeuralNetGraph()

    for input in inputs:
        new_graph.add_input_node(input)


    inputs_m = np.array(inputs, ndmin=2).T
    w1 = np.random.randn(num_hidden_nodes, len(inputs)) * np.sqrt(2 / len(inputs))
    hidden_input = np.dot(w1, inputs_m)
    activation_function = lambda x: scipy.special.expit(x)
    hidden_output = activation_function(hidden_input)

    for hidden_nodes in range(0, num_hidden_nodes):
        new_graph.add_hidden_node(hidden_output)[hidden_node][0]
        for num in range(0, len(inputs)):
            new_graph.add_edge(inputs[num], hidden_output[hidden_node][0], w1[hidden_node][num])


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








