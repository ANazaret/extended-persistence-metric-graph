from simplicial_complex import SimplicialComplex
from bottleneck import *
from graph import Graph
import itertools
import time
import random
import config
import copy

from compass import *

# Vocabulary : shooting points : points added by the discretize function
# eps of the discretization has to be chosen so that for all vertex in the graph p, q dB(p,q) < eps and all the pairwise
# distances inside any barcode is inferior to eps


# Finds smallest distance between each barcodes
def min_dist(barcodes):
    eps = float('inf')
    for i in range(len(barcodes)):
        for j in range(i):
            eps = bottleneck_if_less(barcodes[i], barcodes[j], eps)
    return eps


def graph_min_dist(graph):
    add_inversions(graph)
    barcodes = discrete_barcode_tranform(graph)
    return min_dist(barcodes)


# Barcodes returned from the filtration are of the form : (dim, start, end, type) but we only want start and end.
def compute_barcode(graph, base_point):
    reebified = graph.copy()
    reebified.reebify(base_point)
    filtration = SimplicialComplex.from_graph_extended(reebified, base_point)
    barcode = filtration.get_extended_barcode()
    return [(start, end) for _, start, end, _ in barcode]


# Assumes already discretized
# Computes each barcode
def discrete_barcode_tranform(graph):
    barcodes = []
    for base_point in range(graph.number_of_nodes):
        barcodes.append(compute_barcode(graph, base_point))
    return barcodes


# Look at zero death times
def barcode_arity(barcode):
    assert len(barcode[0]) == 2
    return sum([1 for x, y in barcode if not y]) + 1


# Assumes graph is already reebified and has inversion points
# Adds k points at distance epsilon where k is the arity and k inbetween points when oversampling
def discretize(graph, eps):
    assert graph.is_connected
    for u, v, w in list(graph.iter_edges()):
        shooter1 = graph.insert_point(u, v, eps / w)
        shooter2 = graph.insert_point(v, shooter1, 1/(1-eps/w) - 1)


# Finds epsilon from a set of barcodes
def find_eps(barcodes):
    eps = bottleneck(barcodes[0], barcodes[1])
    for i in range(2, len(barcodes)):
        eps = bottleneck_if_less(barcodes[0], barcodes[i], eps)
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


def find_eps_neighbour(barcodes, eps, alpha):
    neigh = [set() for i in range(len(barcodes))]
    for i in range(len(barcodes)):
        k = barcode_arity(barcodes[i])  # We are looking for k eps neighbours
        j = 0
        while k and j < i:
            if bottleneck_is_less(barcodes[i], barcodes[j], (1+alpha)*eps):
                neigh[i].add(j)
                neigh[j].add(i)
                k -= 1
            j += 1
    return neigh


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


# Caution : might add diagonal points to b1 !
# Assumes b1 and b2 have trivial matching -> condition on eps
# Only b2 can have more point than b1 because b2 is assumed to be a shooting point
# Returns the barcode directions from b1 to b2 in the same order as the barcode points of b1
def barcode_speed(b1, k, b2, precision):
    b2_copy = b2.copy()
    direction = []
    for i, (x,y) in enumerate(b1):
        min_ = float('inf')
        argmin_ = 0
        for j, (xx, yy) in enumerate(b2_copy):
            d = max(abs(xx-x), abs(yy-y))
            if d < min_:
                min_ = d
                argmin_ = j
        xx, yy = b2_copy.pop(argmin_)
        o = ''
        if yy > y + precision:
            o += 'N'
        elif yy < y - precision:
            o += 'S'
        if xx > x + precision :
            o += 'E'
        elif xx < x - precision:
            o += 'W'
        direction.append((i, o))

    # When there are not the same number of points :
    # Remark : won't add 2 times the same point if k > 2
    if b2_copy:
        if k == 1:  # Leaf
            for x,y in b2_copy:
                b1.append((y, y))
                direction.append((len(b1)-1, 'E'))
        else:
            assert k > 2
            for x,y in b2_copy:
                b1.append((x,x))
                direction.append((len(b1)-1, 'S'))

    return direction


# Assumes barcodes and directions are ordered the same way
# Returns whether barcodes b1 and b2 with directions d1 and d2 are aligned
def same_lines(b1, d1, b2, d2, eps):
    d1_copy = copy.deepcopy(d1)
    d2_copy = copy.deepcopy(d2)
    weights = []  # Has meaning only when outputs True, should all be approx the same (to get an idea of numeric err)
    for o in orientations:
        assert len(d1_copy[o]) == len(d2_copy[opposite_orientation(o)])  # Checks opposite speed count check was done
        if o in orientations:
            while d1_copy[o]:
                i = d1_copy[o].pop()
                match = None
                for j in d2_copy[opposite_orientation(o)]:
                    weight = max(abs(b1[i][0]-b2[j][0]), abs(b1[i][1]-b2[j][1]))
                    if is_aligned(o, b1[i], b2[j], eps) and (not weights or abs(weights[-1]-weight) < eps):
                        match = j
                        weights.append(weight)
                        break
                if match is None:
                    return False, weights
                d2_copy[opposite_orientation(o)].remove(match)
    return True, weights


# TODO : change this
# Caution : destroys directions_dict
def shoot(directions_dict, barcodes, eps):
    edges = []
    weights_list = []
    while directions_dict:
        i = random.choice(list(directions_dict.keys()))
        while directions_dict[i]:
            direction_dict = directions_dict[i].pop()  # Taking speed for shooting i to last shooter

            # Finding suspects
            suspects = []
            for j in directions_dict:
                for shooter_id in range(len(directions_dict[j])):
                    if opposite_speed(direction_dict, directions_dict[j][shooter_id]):
                        suspects.append((j, shooter_id))

            # Eliminating suspects
            killer = None
            for j, shooter_id in suspects:
                same, weights = same_lines(barcodes[j], directions_dict[j][shooter_id], barcodes[i], direction_dict, eps)
                if same:
                    killer = j, shooter_id
                    weights_list.append(weights)
                    break

            if killer is not None:
                print("Killer found", i, killer[0])
                directions_dict[killer[0]].pop(killer[1])
                if not directions_dict[killer[0]]:
                    directions_dict.pop(killer[0])
                edges.append((i, killer[0]))
            else:
                print("Killer not found", i)
        directions_dict.pop(i)
    return edges, weights_list


def new_shoot(directions_dict, barcodes, eps):
    edges = []
    weights_list = []
    i = 0
    while directions_dict:
        k = barcode_arity(barcodes[i])
        if k == 2:
            i += 1
            continue

    return edges, weights_list


def graph_to_barcode_set(graph, eps):
    add_inversions(graph)
    discretize(graph, eps)
    return discrete_barcode_tranform(graph)


def barcode_set_to_graph(barcodes, eps, precision):
    measured_eps = find_eps(barcodes)
    fst = find_eps_neighbour(barcodes, measured_eps, 0.2)  # CC Achille
    directions = dict()  # Will only contain directions from
    for i, p in enumerate(fst):
        k = barcode_arity(barcodes[i])
        if len(p) > 1 or k == 1:
            directions[i] = []
            for shooter_id in p:
                    directions[i].append(barcode_speed(barcodes[i], k, barcodes[shooter_id], precision))

    # Filling directions_dict
    # directions_dict[i] is a list of the barcode speed from barcode i to each of its shooting points.
    # a speed is a dictionary whose keys are orientations and values are the index of the starting point
    directions_dict = dict()
    for i, v in directions.items():
        # Initializing directions_dict
        directions_dict[i] = [dict() for j in range(len(v))]
        for j in range(len(v)):
            for o in orientations:
                directions_dict[i][j][o] = []
        for j, shooter_direction in enumerate(v):
            for point_id, orientation in shooter_direction:
                directions_dict[i][j][orientation].append(point_id)

    print(directions_dict[0])
    edges, weights_list = shoot(directions_dict, barcodes, precision)
    graph = Graph()


    # Mainly assigning a new index to each node so that every node is inbetween 0 and graph.number_of_nodes
    bar_to_graph = dict()
    graph_to_bar = dict()
    for j, e in enumerate(edges):
        for i in range(2):
            if e[i] not in bar_to_graph:
                bar_to_graph[e[i]] = graph.number_of_nodes
                graph_to_bar[graph.number_of_nodes] = e[i]
                graph.add_node(graph.number_of_nodes,
                               (random.randint(0, config.WINDOW_SIZE), random.randint(0, config.WINDOW_SIZE)))
        graph.add_edge(bar_to_graph[e[0]], bar_to_graph[e[1]], weights_list[j][0])
    return graph


# Graph -> Barcode Set -> Graph
def test_reconstruction(filename, optimized, oversampling, eps, precision):
    print("Test reconstruction of " + filename)
    graph = load_from_file(filename)
    print('Encoding ...')
    barcodes = graph_to_barcode_set(graph, eps)
    print("Decoding ...")
    reconstructed = barcode_set_to_graph(barcodes, eps, precision)
    print("Edges : ")
    print(reconstructed.nodes)


# Test not using oversampling and just checking cardinality of the edges
def test_weak_version(filename, eps, optimized):
    time_ref = time.clock()
    graph = load_from_file(filename)
    print("Graph loading", time.clock()-time_ref)
    time_ref  = time.clock()
    initial = graph.number_of_nodes
    add_inversions(graph)
    inversions = graph.number_of_nodes
    discretize(graph, eps, False)
    print("Adding points", time.clock() - time_ref)
    time_ref = time.clock()
    discrete = graph.number_of_nodes
    print("Number of nodes : {0} -> {1} -> {2}".format(initial, inversions, discrete))
    barcodes = discrete_barcode_tranform(graph)
    print("Computing all barcodes", time.clock() - time_ref)
    time_ref = time.clock()
    measured_eps = find_eps(barcodes)
    print("Retrieving epsilon ", time.clock() - time_ref)
    time_ref = time.clock()
    if not 0.9*eps < measured_eps < 1.1*eps:
        print("Failed finding eps")
    if optimized:
        fst, _ = find_eps_neighbour_optimized(barcodes, measured_eps, 0.1)
    else:
        fst, _ = find_eps_neighbour(barcodes, measured_eps)
    print("Finding eps neighbourhood", time.clock() - time_ref)
    time_ref = time.clock()
    for i in range(initial):
        if len(graph.nodes[i]) != len(fst[i]):
            print("Error vertex : {0}, {1}, {2}".format(i, len(fst[i]), len(graph.nodes[i])))
    for i in range(initial, inversions):
        if 2 != len(fst[i]):
            print("Error inversion node : {0}, {1}".format(i, len(fst[i])))
    for i in range(inversions, discrete):
        if 1 != len(fst[i]):
            print("Error shooting node: {0}, {1}".format(i, len(fst[i])))
    print("Checking cardinal correctness of eps neighbourhood", time.clock() - time_ref)


# print(graph_min_dist(load_from_file('test_graphs/easy')))  # Outputs 33
# print(graph_min_dist(load_from_file('test_graphs/medium')))  # Outputs 2.1
# print(graph_min_dist(load_from_file('test_graphs/hard')))  # Outputs 0.095
# test_weak_version('test_graphs/easy', 0.1, False)
# test_weak_version('test_graphs/medium', 0.1, False)
# test_weak_version('test_graphs/hard', 0.1, True)  # Errors when decoding
# (points smaller than epsilon or inbetween epsilon and epsilon/2)
# test_weak_version('test_graphs/hard', 0.01, True)  # No error when decoding
test_reconstruction('test_graphs/easy', True, False, 0.1, 0.001)
