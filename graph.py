import collections
import copy
from math import inf


def infinity():
    return inf


class Graph:
    def __init__(self):
        self.nodes = dict()

        self.is_connected = True
        self.distances = dict()

    def add_node(self, node):
        if node not in self.nodes:
            self.nodes[node] = dict()

            self.distances[node] = collections.defaultdict(infinity)
            self.distances[node][node] = 0

            self.is_connected = False

    def add_edge(self, u, v, w):
        self.add_node(u)
        self.add_node(v)
        self.nodes[u][v] = w
        self.nodes[v][u] = w

        self.distances[u][v] = min(w, self.distances[u][v])
        self.distances[v][u] = self.distances[u][v]

        maximum = -1
        for n in self.nodes:
            self.distances[u][n] = min(self.distances[u][n], self.distances[u][v] + self.distances[v][n])
            self.distances[n][u] = self.distances[u][n]
            self.distances[v][n] = min(self.distances[v][n], self.distances[v][u] + self.distances[u][n])
            self.distances[n][v] = self.distances[v][n]
            maximum = max(maximum, self.distances[v][n])

        self.is_connected = maximum != inf

    def __getitem__(self, item):
        return self.nodes[item]

    @property
    def number_of_nodes(self):
        return len(self.nodes)

    def iter_edges(self):
        for u in self.nodes:
            for v in self.nodes[u]:
                if u < v:
                    yield (u, v, self.nodes[u][v])

    def copy_and_insert_base_point(self, u, v, alpha):
        graph = Graph()
        graph.nodes = copy.deepcopy(self.nodes)
        graph.distances = copy.deepcopy(self.distances)

        new_point = graph.number_of_nodes
        graph.add_node(new_point)
        graph.add_edge(u, new_point, alpha * graph.distances[u][v])
        graph.add_edge(v, new_point, (1 - alpha) * graph.distances[u][v])

        # Remove edge u -> v (doesn't change distances because u->n->v is the same)
        graph.nodes[u].pop(v)
        graph.nodes[v].pop(u)

        return graph, new_point
