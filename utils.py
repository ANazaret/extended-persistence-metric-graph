from config import EPSILON
from graph import Graph
from simplicial_complex import SimplicialComplex


def map_barcode_to_graph_vertices(barcode, filtration: SimplicialComplex, graph: Graph, base_point):
    barcode_mapping = dict()
    infinity = filtration.extended_infinity
    distances = graph.distances[base_point]

    for interval in barcode:
        dimension, start, end, _ = interval

        vertices = [None, None]
        if dimension == 0:
            max_d, mav_v = -1, None
            for v, distance in distances.items():
                if abs(distance) < EPSILON:
                    vertices[0] = v
                if distance > max_d:
                    max_d = distance
                    mav_v = v
            vertices[1] = mav_v

        for v, distance in distances.items():
            if abs(distance - start) < EPSILON:
                vertices[0] = v
            if abs(distance - end) < EPSILON:
                vertices[1] = v
            if abs(distance - 2 * infinity + start) < EPSILON:
                vertices[0] = v
            if abs(distance - 2 * infinity + end) < EPSILON:
                vertices[1] = v
        barcode_mapping[interval] = vertices

    return barcode_mapping
