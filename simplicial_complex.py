import collections
import math
from typing import Tuple, Iterator

from datamodels import IntervalType
from graph import Graph
from matrix import Matrix

Vertex = int
Simplex = collections.namedtuple('Simplex', ['appearance', 'dimension', 'vertices'])


def iter_facets(simplex: Simplex) -> Iterator[Tuple[Vertex]]:
    if simplex.dimension == 0:
        return

    for v in simplex.vertices:
        subset = tuple([w for w in simplex.vertices if w != v])
        yield subset


class SimplicialComplex:
    def __init__(self):
        self.simplicies = []
        self.simplicies_indexes = dict()

        self.extended_infinity = None

    @staticmethod
    def from_graph_extended(graph: Graph, base_point) -> "SimplicialComplex":
        sc = SimplicialComplex()

        distances = graph.distances[base_point]

        # Insert vertices (ordinary persistence)
        maxi = 0
        for v, d in distances.items():
            maxi = max(maxi, d)
            sc.add_simplex(Simplex(d, 0, [v]))

        # Insert edges of ordinary persistence
        for u, v, _ in graph.iter_edges():
            sc.add_simplex(Simplex(max(distances[u], distances[v]), 1, [u, v]))

        # Insert infinity point at time maxi (remove it from the barcode, dim = 0)
        maxi += 5
        infinity_point = graph.number_of_nodes
        sc.add_simplex(Simplex(maxi, 0, [infinity_point]))
        maxi += 5

        # Insert edges of extended persistence (link vertices to infinity_point)
        for v, d in distances.items():
            sc.add_simplex(Simplex(2 * maxi - d, 1, [v, infinity_point]))

        # Insert faces of relative persistence (link edges to infinity_point)
        for u, v, _ in graph.iter_edges():
            sc.add_simplex(Simplex(2 * maxi - min(distances[u], distances[v]), 2, [u, v, infinity_point]))

        sc.extended_infinity = maxi
        sc.__init_indexes()
        return sc

    def __init_indexes(self):
        self.simplicies.sort()
        self.update_indexes()

    def update_indexes(self):
        self.simplicies_indexes = dict([(tuple(s.vertices), i) for i, s in enumerate(self.simplicies)])

    def add_simplex(self, simplex: Simplex):
        self.simplicies.append(simplex)

    def compute_boundary_matrix(self):
        matrix = Matrix(len(self.simplicies))
        for i, s in enumerate(self.simplicies):
            for facet in iter_facets(s):
                matrix.set_one(self.simplicies_indexes[facet], i)
        return matrix

    def get_extended_barcode(self):
        boundary_matrix = self.compute_boundary_matrix()
        pivots = boundary_matrix.reduce()

        # Fix extended persistence trick that changes the time value
        def to_extended(dimension_, start_, end_):
            interval_type = IntervalType.from_tricked_interval(start_, end_, self.extended_infinity)
            if end_ == math.inf:
                end_ = self.extended_infinity
            if start_ > self.extended_infinity:
                start_ = 2 * self.extended_infinity - start_
            if end_ > self.extended_infinity:
                end_ = 2 * self.extended_infinity - end_

            return dimension_, start_, end_, interval_type

        intervals = []
        zero_columns = boundary_matrix.get_zero_columns()
        for j in sorted(zero_columns):
            simplex = self.simplicies[j]
            if j in pivots:
                simplex_killer = self.simplicies[pivots[j]]
                if simplex_killer.appearance <= simplex.appearance:
                    continue
                end = simplex_killer.appearance
            else:
                end = math.inf

            if self.extended_infinity - 2 > simplex.appearance > self.extended_infinity - 8:
                # Remove the interval created by infinity point
                continue
            intervals.append(to_extended(simplex.dimension, simplex.appearance, end))

        return intervals

    def describe(self):
        return collections.Counter(map(lambda x: x.dimension, self.simplicies))
