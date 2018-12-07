import collections
import copy
from math import inf

from config import EPSILON


def infinity():
    return inf


class Graph:
    def __init__(self):
        self.nodes = dict()
        self.node_positions = dict()

        self.is_connected = True
        self.distances = dict()

        self.number_of_edges = 0

    def add_node(self, node, position):
        if node not in self.nodes:
            self.nodes[node] = dict()
            self.node_positions[node] = position

            self.distances[node] = collections.defaultdict(infinity)
            self.distances[node][node] = 0

            self.is_connected = False

    def add_edge(self, u, v, w):
        # Assume u, v already exist !
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

        self.number_of_edges += 1

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

    def reebify(self, base_point):
        # Critical point on edge (u,v)
        # iff \exists alpha \in ]0, w_uv[, d[u] + alpha*w_uv = d[v] + (1_alpha)*w_uv

        distances = self.distances[base_point]
        points_to_add = []
        for u, v, w in self.iter_edges():
            alpha = (1 + (distances[v] - distances[u]) / w) / 2
            if EPSILON < alpha < 1 - EPSILON:
                points_to_add.append((u, v, alpha))

        for p in points_to_add:
            self.insert_point(*p)

    def insert_point(self, u, v, alpha):
        new_point = self.number_of_nodes
        self.add_node(new_point, (1 - alpha) * self.node_positions[u] + alpha * self.node_positions[v])
        self.add_edge(u, new_point, alpha * self.distances[u][v])
        self.add_edge(v, new_point, (1 - alpha) * self.distances[u][v])

        # Remove edge u -> v (doesn't change distances because u->n->v is the same)
        self.nodes[u].pop(v)
        self.nodes[v].pop(u)
        return new_point

    def copy(self):
        graph = Graph()
        graph.nodes = copy.deepcopy(self.nodes)
        graph.node_positions = copy.deepcopy(self.node_positions)
        graph.distances = copy.deepcopy(self.distances)
        return graph
