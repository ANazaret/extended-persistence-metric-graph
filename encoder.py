from simplicial_complex import SimplicialComplex
from bottleneck import *
import itertools


def graph_min_dist(graph):
    add_inversions(graph)
    barcodes = discrete_barcode_tranform(graph)
    return min_dist(barcodes)


# Finds smallest distance between each barcodes
def min_dist(barcodes):
    eps = float('inf')
    for i in range(len(barcodes)):
        for j in range(i):
            eps = bottleneck_if_less(barcodes[i], barcodes[j], eps)
    return eps


# Assumes already discretized
# Computes each barcode
def discrete_barcode_tranform(graph):
    barcodes = []
    for base_point in range(graph.number_of_nodes):
        barcodes.append(compute_barcode(graph, base_point))
    return barcodes


# Barcodes returned from the filtration are of the form : (dim, start, end, type) but we only want start and end.
def compute_barcode(graph, base_point):
    reebified = graph.copy()
    reebified.reebify(base_point)
    filtration = SimplicialComplex.from_graph_extended(reebified, base_point)
    barcode = filtration.get_extended_barcode()
    return [(start, end) for _, start, end, _ in barcode]


def graph_to_barcode_set(graph, eps):
    a = graph.number_of_nodes
    add_inversions(graph)
    b = graph.number_of_nodes
    discretize(graph, eps)
    c = graph.number_of_nodes
    print('Graph nodes : {} -> {} ->  {}'.format(a,b,c))
    return discrete_barcode_tranform(graph)


# Assumes graph is already reebified and has inversion points
# Adds k points at distance epsilon where k is the arity and k inbetween points when oversampling
def discretize(graph, eps):
    assert graph.is_connected
    for u, v, w in list(graph.iter_edges()):
        shooter1 = graph.insert_point(u, v, eps / w)
        graph.insert_point(v, shooter1, 1/(1-eps/w) - 1)


# Adds yellow points
def add_inversions(graph):
    for u, v in list(itertools.combinations(graph.nodes.keys(), 2)):
        if len(graph.nodes[u]) == 2 or len(graph.nodes[v]) == 2:
            continue
        for a, b, dab in list(graph.iter_edges(True)):
            if (graph.distances[a][u] <= graph.distances[a][v] and
                    graph.distances[b][v] <= graph.distances[b][u]):
                daw = (dab + graph.distances[b][v] - graph.distances[a][u]) / 2
                daw /= dab
                if not (0 <= daw <= 1):
                    print("FOCK")
                    print(daw)
                else:
                    graph.insert_point(a, b, daw)
