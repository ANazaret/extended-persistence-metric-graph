import collections
import copy
from math import inf

from config import EPSILON


def infinity():
    return inf


class Graph:
    def __init__(self):
        self.nodes = dict()  # Abel : edges weight
        self.node_positions = dict()

        self.is_connected = True
        self.distances = dict()

        self.number_of_edges = 0
        self.base_point_reeb = None

    def add_node(self, node, position):
        if node not in self.nodes:
            self.nodes[node] = dict()
            self.node_positions[node] = position

            self.distances[node] = collections.defaultdict(infinity)
            self.distances[node][node] = 0

            self.is_connected = False

    def remove_val_2_node(self, node):

        # Abel : erasing edges
        neighbors = self.nodes.pop(node)
        w = 0
        for u in neighbors:  # Abel : supposed to be of size 2
            w += self.nodes[u].pop(node)

        u, v = neighbors.keys()
        self.add_edge(u, v, w)

        # Abel : ersaing the rest
        self.node_positions.pop(node)
        self.distances.pop(node)
        for d in self.nodes:
            self.distances[d].pop(node)

    def add_edge(self, u, v, w):
        # Assume u, v already exist !
        self.nodes[u][v] = w
        self.nodes[v][u] = w

        self.distances[u][v] = min(w, self.distances[u][v])
        self.distances[v][u] = self.distances[u][v]

        #Abel : updates other distances
        maximum = -1
        for i in range(len(self.nodes)):
            for j in range(i):
                self.distances[i][j] = min([
                    self.distances[i][j],
                    self.distances[i][u] + w + self.distances[v][j],
                    self.distances[i][v] + w + self.distances[u][j]
                ])
                self.distances[j][i] = self.distances[i][j]
                maximum = max(maximum, self.distances[i][j])

        self.is_connected = maximum != inf
        self.number_of_edges += 1

    def __getitem__(self, item):
        return self.nodes[item]

    def has_edge(self, u, v):
        return u in self.nodes and v in self.nodes[u]

    @property
    def number_of_nodes(self):
        return len(self.nodes)

    # Abel : both = (u,v) and (v,u)
    def iter_edges(self, both=False):
        for u in self.nodes:
            for v in self.nodes[u]:
                if both or u < v:
                    yield (u, v, self.nodes[u][v])

    def set_basepoint(self, base_point):
        if base_point[1]:
            u, v, alpha = base_point[2]
            base_point = self.insert_point(u, v, alpha)
        else:
            base_point = base_point[2]
        self.base_point_reeb = base_point
        return base_point

    def reebify(self, base_point, delete_base_point=False):
        # Critical point on edge (u,v)
        # iff \exists alpha \in ]0, w_uv[, d[u] + alpha*w_uv = d[v] + (1_alpha)*w_uv

        distances = self.distances[base_point]
        points_to_add = []
        for u, v, w in self.iter_edges():
            alpha = (1 + (distances[v] - distances[u]) / w) / 2
            if EPSILON < alpha < 1 - EPSILON:
                points_to_add.append((u, v, alpha))

        if delete_base_point:
            self.remove_val_2_node(base_point)

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
