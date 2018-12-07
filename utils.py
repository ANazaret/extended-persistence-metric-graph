from config import EPSILON
from graph import Graph
from simplicial_complex import SimplicialComplex


def map_barcode_to_graph_vertices(barcode, filtration: SimplicialComplex, graph: Graph, base_point):
    barcode_mapping = dict()
    infinity = filtration.extended_infinity
    distances = graph.distances[base_point]

    for interval in barcode:
        d, s, e, t = interval
        if d == 0:
            continue

        vertices = [None, None]
        for v, d in distances.items():
            if abs(d - s) < EPSILON:
                vertices[0] = v
            if abs(d - e) < EPSILON:
                vertices[1] = v
            if abs(d - 2 * infinity + s) < EPSILON:
                vertices[0] = v
            if abs(d - 2 * infinity + e) < EPSILON:
                vertices[1] = v
        barcode_mapping[interval] = vertices

    return barcode_mapping
