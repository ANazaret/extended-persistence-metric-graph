from config import EPSILON
from graph import Graph
from simplicial_complex import SimplicialComplex


def map_barcode_to_graph_vertices(barcode, filtration: SimplicialComplex, graph: Graph, base_point):
    barcode_mapping = dict()
    infinity = filtration.extended_infinity
    distances = graph.distances[base_point]

    for interval in barcode:
        dimension, start, end, _ = interval
        if dimension == 0:
            continue

        vertices = [None, None]
        for v, dimension in distances.items():
            if abs(dimension - start) < EPSILON:
                vertices[0] = v
            if abs(dimension - end) < EPSILON:
                vertices[1] = v
            if abs(dimension - 2 * infinity + start) < EPSILON:
                vertices[0] = v
            if abs(dimension - 2 * infinity + end) < EPSILON:
                vertices[1] = v
        barcode_mapping[interval] = vertices

    return barcode_mapping
