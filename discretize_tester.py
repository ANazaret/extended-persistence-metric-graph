import time
from encoder import *
from decoder import *


# Graph -> Barcode Set -> Graph
def test_reconstruction(filename, eps, precision):
    print("Test reconstruction of " + filename)
    print("")

    print("Loading")
    ref_time = time.clock()
    graph = load_from_file(filename)
    print('Done in ', time.clock() - ref_time)
    print("")

    ref_time = time.clock()
    print('Encoding ...')
    barcodes = graph_to_barcode_set(graph, eps)
    print('Done in ', time.clock() - ref_time)
    print("")

    ref_time = time.clock()
    print("Decoding ...")
    reconstructed = barcode_set_to_graph(barcodes, precision)
    print('Done in ', time.clock() - ref_time)
    print("")

    print("Graph : ")
    print(reconstructed.nodes)


# Test not using oversampling and just checking cardinality of the edges
def test_cardinality(filename, eps):
    time_ref = time.clock()
    graph = load_from_file(filename)
    print("Graph loading", time.clock()-time_ref)
    time_ref  = time.clock()
    initial = graph.number_of_nodes
    add_inversions(graph)
    inversions = graph.number_of_nodes
    discretize(graph, eps)
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
    fst = find_eps_neighbour(barcodes, measured_eps, 0.1)
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
# test_cardinality('test_graphs/hard', 0.01)
# test_cardinality('test_graphs/medium', 0.1)
# test_cardinality('test_graphs/hard', 0.1)  # Errors when decoding
# test_cardinality('test_graphs/hard', 0.01)  # No error when decoding


# test_reconstruction('test_graphs/hard', 0.01, 0.001)
test_reconstruction('test_graphs/easy', 0.1, 0.001)