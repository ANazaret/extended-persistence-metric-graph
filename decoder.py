import random
import config
from bottleneck import *
from compass import *


def barcode_set_to_graph(barcodes, precision):
    measured_eps = find_eps(barcodes)
    eps_neigh = find_eps_neighbour(barcodes, measured_eps, 0.2)  # CC Achille
    arities = dict()
    unmatched_arity_2 = []

    # Filling directions and unmatched_arity_2
    # directions[i] is None if i is of arity 2 and is a list of couples : (shooter_id, direction) otherwise
    # where shooter_id are all the points in the eps_neigh of i
    directions = dict()
    for i, p in enumerate(eps_neigh):
        arities[i] = barcode_arity(barcodes[i])
        if arities[i] != 2:  # We don't need the directions of the others for now, but we'll need them after
            directions[i] = dict()
            for shooter_id in p:
                    directions[i][shooter_id] = barcode_speed(barcodes[i], arities[i], barcodes[shooter_id], precision)
        else:
            unmatched_arity_2.append(i)

    edges = shoot(barcodes, directions, unmatched_arity_2, arities, eps_neigh, precision)
    print(edges)
    return reconstruct_graph(edges)


# Finds epsilon from a set of barcodes
def find_eps(barcodes):
    eps = bottleneck(barcodes[0], barcodes[1])
    for i in range(2, len(barcodes)):
        eps = bottleneck_if_less(barcodes[0], barcodes[i], eps)
    return eps


# Finds the epsilon neighbourhood of each barcode, alpha is a precision factor
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


# Link points by shooting
# Takes one by one the remaining points of arity different than 2
# For the untreated directions of this base_shooter_point, shoot while you fall on arity 2 point
# The more you have shot the less barcodes you have to test
# Caution : for this reason unmatched_arity_2 and directions are progressively destroyed
# Returns the edges with the weights
def shoot(barcodes, directions, unmatched_arity_2, arities, eps_neigh, precision):
    edges = []

    print("")
    while directions:

        # Select a base_shooter
        base_shooter_id = random.choice(list(directions.keys()))
        print("Base shooter is now ", base_shooter_id)
        directions_of_ref = directions[base_shooter_id]

        # Iterating over the aiming directions (=aiming_pt_id) from base_shooter
        while directions_of_ref:
            aiming_pt_id = random.choice(list(directions_of_ref.keys()))
            direction = directions_of_ref.pop(aiming_pt_id)
            shooter_id = base_shooter_id
            print("Aiming point id is ", aiming_pt_id)

            # Cleaning
            if not directions[base_shooter_id]:
                directions.pop(base_shooter_id)

            # Breaks when arrived on a point of arity different than 2
            arrived = False
            while not arrived:
                barcodes_to_test = [j for j in range(len(barcodes)) if j not in [shooter_id, aiming_pt_id]
                                    and (j in unmatched_arity_2 or j in directions.keys())]

                match_id, weight = match_barcodes(shooter_id, direction, barcodes, barcodes_to_test, precision)
                assert len(eps_neigh[match_id]) == 1  # Assert this point is an aiming point
                next_shooter_id = list(eps_neigh[match_id])[0]
                edge = (shooter_id, next_shooter_id, weight)
                edges.append(edge)
                print("Added edge : ", edge)
                shooter_id = next_shooter_id

                # If we reached a point with arity diff than 2
                if arities[shooter_id] != 2:
                    print("Shoot arrived at : ", shooter_id)
                    print(" ")
                    # Removes direction from shooter_id
                    directions[shooter_id].pop(match_id)
                    if not directions[shooter_id]:
                        directions.pop(shooter_id)
                    arrived = True

                # Otherwise continue by finding next shooter point and computing the correspondent speed
                else:
                    unmatched_arity_2.remove(shooter_id)
                    a, b = list(eps_neigh[shooter_id])
                    if a == match_id:
                        aiming_pt_id = b
                    else:
                        assert b == match_id
                        aiming_pt_id = a
                    direction = barcode_speed(barcodes[shooter_id], arities[shooter_id], barcodes[aiming_pt_id], precision)
        print("")
    return edges


# Returns the "nearest" barcode from ref_barcode shooting with ref_direction
# To do so, first finds suspects (= have one point aligned with some fixed point of ref_barcode and compute
# the distance with these 2 points)
# Then order those suspects by the distance and for all ref_barcode points try to find a match at app. this distance in
# the suspect barcode.
# Returns the first one we found = the nearest
def match_barcodes(ref_barcode_id, ref_direction, barcodes,  barcodes_to_test, precision):
    ref_barcode = barcodes[ref_barcode_id]
    base_point = random.randint(0, len(ref_barcode[0])-1)  # TODO : randomize everywhere or just one time ?
    suspects = []

    for i in barcodes_to_test:
        b = barcodes[i]
        min_ = float('inf')  # min_ will contain the supposed drift distance
        for j, q in enumerate(b):
            if is_aligned(ref_direction[base_point][1], ref_barcode[base_point], q, precision):
                d = inf_dist(ref_barcode[base_point], q)
                if d < min_:
                    min_ = d

        if min_ != float('inf'):  # Means we found a suspect
            suspects.append((i, min_))

    if not suspects:
        raise ValueError('No suspects for ', ref_barcode_id, barcodes_to_test)

    suspects.sort(key=lambda x: x[1])  # We want to find the nearest

    for i, min_ in suspects:
        b_copy = barcodes[i].copy()
        for j, p in enumerate(ref_barcode):
            match = -1
            for k, q in enumerate(b_copy):
                if is_aligned(ref_direction[j][1], p, q, precision) and abs(inf_dist(p, q) - min_) < precision:
                    match = k
                    break
            if match != -1:
                b_copy.pop(match)
            else:
                break
        if not b_copy:  # Means we matched all points
            return i, min_

    raise ValueError('Matching barcode not found {0} , {1}, {2}'.format(ref_barcode, barcodes_to_test, precision))


# Mainly assigning a new index to each node so that every node is inbetween 0 and graph.number_of_nodes
def reconstruct_graph(edges):
    graph = Graph()
    bar_to_graph = dict()
    graph_to_bar = dict()
    for j, e in enumerate(edges):
        for i in range(2):
            if e[i] not in bar_to_graph:
                bar_to_graph[e[i]] = graph.number_of_nodes
                graph_to_bar[graph.number_of_nodes] = e[i]
                graph.add_node(graph.number_of_nodes,
                               (random.randint(0, config.WINDOW_SIZE), random.randint(0, config.WINDOW_SIZE)))
        graph.add_edge(bar_to_graph[e[0]], bar_to_graph[e[1]], e[2])
    return graph


# Look at zero death times
def barcode_arity(barcode):
    assert len(barcode[0]) == 2
    return sum([1 for x, y in barcode if not y]) + 1