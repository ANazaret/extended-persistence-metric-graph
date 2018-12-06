

class Graph:
    def __init__(self):
        self.nodes = dict()

    def add_node(self, node):
        if node not in self.nodes:
            self.nodes[node] = dict()

    def add_edge(self, u, v, w):
        self.add_node(u)
        self.add_node(v)
        self.nodes[u][v] = w
        self.nodes[v][u] = w

    def __getitem__(self, item):
        return self.nodes[item]

    @property
    def number_of_nodes(self):
        return len(self.nodes)

    def iter_edges(self):
        for u in self.nodes:
            for v in self.nodes[u]:
                if u < v:
                    yield (u,v,self.nodes[u][v])