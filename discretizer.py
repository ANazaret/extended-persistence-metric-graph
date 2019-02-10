from simplicial_complex import SimplicialComplex
from bottleneck import bottleneck, bottleneck_if_less, bottleneck_is_between
from graph import Graph
import numpy as np
import itertools
import time

# Vocabulary : shooting points : points added by the discretize function

# Barcodes returned from the filtration are of the form : (dim, start, end, type) but we only want start and end.
def compute_barcode(graph, base_point):
    reebified = graph.copy()
    reebified.reebify(base_point)
    filtration = SimplicialComplex.from_graph_extended(reebified, base_point)
    barcode = filtration.get_extended_barcode()
    return [(start, end) for _, start, end, _ in barcode]


# Assumes graph is already reebified and has inversion points
# Adds k points at distance epsilon where k is the arity
def discretize(graph, eps):
    assert graph.is_connected
    for u, v, w in list(graph.iter_edges()):
        new_point = graph.insert_point(u, v, eps / w)
        graph.insert_point(v, new_point, 1/(1-eps/w) - 1)


# Assumes already discretized
# Computes each barcode
def discrete_barcode_tranform(graph):
    barcodes = []
    for base_point in range(graph.number_of_nodes):
        barcodes.append(compute_barcode(graph, base_point))
    return barcodes


# Finds epsilon from a set of barcodes
def find_eps(barcodes):
    eps = bottleneck(barcodes[0], barcodes[1])
    nearest = 1
    for i in range(2, len(barcodes)):
        new_eps = bottleneck_if_less(barcodes[0], barcodes[i], eps)
        if new_eps != eps:
            eps = new_eps
            nearest = i
    return eps



# TODO : optimize

# Optimizations under the Nazaret assumption:
# A : Look at the arity of the node, it gives us the number of eps neighbours -> we can stop once we
# found them -> divide by 2 the complexity constant
# B : if b has strictly more than 1 eps neigbour, all its eps neighbours are shooting points,
#  hence they only have 1 eps neighbour. Reciprocally, if a point has only one eps neighbour than it is either a
# leaf or a shooting point (distinguished by arity). Therefore, when we get a non shooting point, we get rid
#  of k+1 points at once (k is the arity of the node) and when we get a shooting point we get
# to know a non shooting point.

# Optimizations in the "general" case :
# C : triangular inequality

# Finds eps-neighbourhood of each barcode
def find_eps_neighbour(barcodes, eps):
    first_neigh, sec_neigh = [set() for i in range(len(barcodes))], [set() for i in range(len(barcodes))]
    for i in range(len(barcodes)):
        for j in range(i):
            d = bottleneck_if_less(barcodes[i], barcodes[j], 4*eps)
            if 0.5 * eps < d < 1.5*eps:
                first_neigh[i].add(j)
                first_neigh[j].add(i)
            elif 1.5 * eps <= d < 2.5*eps:
                sec_neigh[i].add(j)
                sec_neigh[j].add(i)
            elif 3.5*eps < d:
                pass
            else:
                print("Should not happen")
                print(d)
    return first_neigh, sec_neigh


def find_eps_neighbour_optimized(barcodes, eps, alpha):
    first_neigh, sec_neigh = [set() for i in range(len(barcodes))], [set() for i in range(len(barcodes))]
    for i in range(len(barcodes)):
        for j in range(i):
            location = bottleneck_is_between(barcodes[i], barcodes[j], ((1-alpha)*eps, (1+alpha)*eps), ((2-alpha)*eps, (2+alpha)*eps))
            if location == 'I1':
                first_neigh[i].add(j)
                first_neigh[j].add(i)
            elif location == 'I2':
                sec_neigh[i].add(j)
                sec_neigh[j].add(i)
            elif location == 'G':
                continue
            else:
                print("Numeric Error in find_eps_neighbour_optimized : " + location)
    return first_neigh, sec_neigh


def barcode_set_to_graph(barcodes):
    pass


def load_from_file(filename):
    graph = Graph()
    with open(filename, 'r') as f:
        n, e = map(int, f.readline().split(','))
        for i in range(n):
            x, y = map(int, f.readline().split(','))
            node = graph.number_of_nodes
            graph.add_node(node, np.array([x, y]))
        for _ in range(e):
            u, v = map(int, f.readline().split(','))
            if u > v:
                u, v = v, u
            ux, uy = graph.node_positions[u]
            vx, vy = graph.node_positions[v]
            w = ((ux - vx) ** 2 + (uy - vy) ** 2) ** 0.5
            graph.add_edge(u, v, w)
    return graph


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


# Test using only k shooting points with k being the arity of the node
def test_weak_version(filename, eps, optimized):
    deb = time.clock()
    times = [("Start", 0)]
    print(times[-1])

    graph = load_from_file(filename)
    times.append(("Graph loading", time.clock()-times[-1][1]))
    print(times[-1])

    initial = graph.number_of_nodes
    add_inversions(graph)
    inversions = graph.number_of_nodes
    discretize(graph, 0.1)
    times.append(("Adding points", time.clock()-times[-1][1]))
    print(times[-1])

    discrete = graph.number_of_nodes
    print("Number of nodes : {0} -> {1} -> {2}".format(initial, inversions, discrete))
    barcodes = discrete_barcode_tranform(graph)
    times.append(("Computing all barcodes", time.clock()-times[-1][1]))
    print(times[-1])

    measured_eps = find_eps(barcodes)
    times.append(("Finding epsilon", time.clock() - times[-1][1]))
    print(times[-1])

    if not 0.9*eps < measured_eps < 1.1*eps:
        print("Failed finding eps")
    if optimized:
        fst, _ = find_eps_neighbour_optimized(barcodes, measured_eps, 0.1)
    else:
        fst, _ = find_eps_neighbour(barcodes, measured_eps)
    times.append(("Finding eps neighbourhood", time.clock() - times[-1][1]))
    print(times[-1])

    for i in range(initial):
        if len(graph.nodes[i]) != len(fst[i]):
            print("Error vertex : {0}, {1}, {2}".format(i, len(fst[i]), len(graph.nodes[i])))
    for i in range(initial, inversions):
        if 2 != len(fst[i]):
            print("Error inversion node : {0}, {1}".format(i, len(fst[i])))
    for i in range(inversions, discrete):
        if 1 != len(fst[i]):
            print("Error shooting node: {0}, {1}".format(i, len(fst[i])))
    times.append(("Checking correctness of epsilon neighbourhood", time.clock() - times[-1][1]))
    print(times[-1])


# test_weak_version('test_graphs/easy', 0.1)
test_weak_version('test_graphs/medium', 0.1, False)
# test_weak_version('test_graphs/hard', 0.1, True)