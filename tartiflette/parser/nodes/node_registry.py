from typing import List


class NodeRegistry:
    def __init__(self):
        self.nodes: List[List[NodeField]] = []
        self._current_level = 0
        self._nb_level = 0

    def add_node(self, index: int, node):
        try:
            self.nodes[index]
        except IndexError:
            self._nb_level = self._nb_level + 1
            self.nodes.append([])

        self.nodes[index].append(node)

    def add_next_level_node(self, node):
        self.add_node(self.current_level + 1, node)

    def next_level(self):
        self._current_level = self._current_level + 1
        return self.nodes[self.current_level]

    def has_next(self):
        return self.current_level < self._nb_level - 1

    @property
    def current_level(self):
        return self._current_level - 1

    @property
    def root_nodes(self):
        return self.nodes[0]

    def remove_node(self, node):
        for index, _nodes in enumerate(self.nodes):
            self.nodes[index] = [n for n in _nodes if n != node]
