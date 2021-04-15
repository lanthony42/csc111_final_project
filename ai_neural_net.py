from __future__ import annotations

from typing import Union
import scipy.special


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

    def add_input_node(self) -> None:
        """Add an input node with the given number to this graph.

        The new input node is not adjacent to any other vertices.
        """
        self.curr_num += 1
        new_vertex = _WeightedVertex(self.curr_num, 'input')

        self._vertices[self.curr_num] = new_vertex
        self.input_nodes.append(new_vertex)

    def add_hidden_node(self) -> None:
        """Add a hidden node with the given item to this graph.

        The new hidden node is not adjacent to any other vertices.
        """
        self.curr_num += 1
        new_vertex = _WeightedVertex(self.curr_num, 'hidden')
        self._vertices[self.curr_num] = new_vertex

    def add_output_node(self) -> None:
        """Add an output node with the given item to this graph.

        The new output node is not adjacent to any other vertices.
        """
        self.curr_num += 1
        new_vertex = _WeightedVertex(self.curr_num, 'output')

        self._vertices[self.curr_num] = new_vertex
        self.output_nodes.append(new_vertex)

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


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['scipy.special'],
        'max-line-length': 100,
        'disable': ['E1136', 'E1101']
    })

    import python_ta.contracts
    python_ta.contracts.DEBUG_CONTRACTS = True
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()
