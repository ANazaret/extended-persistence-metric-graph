import networkx as nx


# Returns true if dB(b1,b2) <= sup
def bottleneck_is_less(b1, b2, sup):
    dists = barcode_distances(b1, b2)
    n1, n2 = len(b1), len(b2)

    # Initializing Bipartite
    G = nx.Graph()
    G.add_nodes_from([('b1', i) for i in range(n1)], bipartite=0)
    G.add_nodes_from([('b2_proj', i) for i in range(n2)], bipartite=0)
    G.add_nodes_from([('b2', i) for i in range(n2)], bipartite=1)
    G.add_nodes_from([('b1_proj', i) for i in range(n1)], bipartite=1)
    top_nodes = [('b1', i) for i in range(n1)] + [('b2_proj', i) for i in range(n2)]

    n = n1 + n2
    count = 0
    while count < len(dists) and dists[count][2] <= sup:
        G.add_edge(dists[count][0], dists[count][1])
        count += 1

    matching = nx.bipartite.maximum_matching(G, top_nodes)
    if len(matching) < 2 * n:
        return False
    return True


# Convention :
# - U : b1 , b2_proj
# - V : b2, b1_proj
def barcode_distances(b1, b2):
    b1_proj = []  # Projection of b1 points on the diagonal
    b2_proj = []  # Projection of b2 points on the diagonal
    for s, e in b1:
        b1_proj.append(((s + e) / 2, (s + e) / 2))
    for s, e in b2:
        b2_proj.append(((s + e) / 2, (s + e) / 2))

    dists = []
    for i, (s, e) in enumerate(b1):
        for j, (s2, e2) in enumerate(b2):
            dists.append((('b1', i), ('b2', j), max(abs(s - s2), abs(e - e2))))
        for j, (s2, e2) in enumerate(b1_proj):
            dists.append((('b1', i), ('b1_proj', j), max(abs(s - s2), abs(e - e2))))
    for i, (s, e) in enumerate(b2_proj):
        for j, (s2, e2) in enumerate(b2):
            dists.append((('b2_proj', i), ('b2', j), max(abs(s - s2), abs(e - e2))))
        for j, (s2, e2) in enumerate(b1_proj):
            dists.append((('b2_proj', i), ('b1_proj', j), 0))

    dists.sort(key= lambda x: x[2])
    return dists


# If the bottleneck distance is greater than sup, returns sup
# Otherwise, performs dichotomy to find true bottleneck distance
def bottleneck_if_less(b1, b2, sup):
    dists = barcode_distances(b1, b2)
    n1, n2 = len(b1), len(b2)

    # Initializing Bipartite
    G = nx.Graph()
    G.add_nodes_from([('b1', i) for i in range(n1)], bipartite=0)
    G.add_nodes_from([('b2_proj', i) for i in range(n2)], bipartite=0)
    G.add_nodes_from([('b2', i) for i in range(n2)], bipartite=1)
    G.add_nodes_from([('b1_proj', i) for i in range(n1)], bipartite=1)
    top_nodes = [('b1', i) for i in range(n1)] + [('b2_proj', i) for i in range(n2)]

    n = n1 + n2
    under_sup = []
    count = 0
    while count < len(dists) and dists[count][2] <= sup:
        under_sup.append(dists[count])
        G.add_edge(dists[count][0], dists[count][1])
        count += 1

    matching = nx.bipartite.maximum_matching(G, top_nodes)
    if len(matching) < 2*n:
        return sup

    # Dichotomy
    down, mid, up = 0, len(under_sup)//2, len(under_sup)
    G.remove_edges_from(list(G.edges.keys()))
    for i in range(mid):
        G.add_edge(dists[i][0], dists[i][1])

    step = 0
    while down < mid < up:
        matching = nx.bipartite.maximum_matching(G, top_nodes)
        if len(matching) < 2*n:
            down = mid
            mid = (down + up) // 2
            # Add edges from old mid (=down) to new mid
            for i in range(down, mid):
                G.add_edge(dists[i][0], dists[i][1])
        else:
            up = mid
            mid = (down + up) // 2
            # Removes all edges and add until mid
            G.remove_edges_from(list(G.edges.keys()))
            for i in range(mid):
                G.add_edge(dists[i][0], dists[i][1])
        step += 1
    return dists[mid][2]


def bottleneck(b1, b2):
    dists = barcode_distances(b1, b2)
    n1, n2 = len(b1), len(b2)

    # Initializing Bipartite
    G = nx.Graph()
    G.add_nodes_from([('b1', i) for i in range(n1)], bipartite=0)
    G.add_nodes_from([('b2_proj', i) for i in range(n2)], bipartite=0)
    G.add_nodes_from([('b2', i) for i in range(n2)], bipartite=1)
    G.add_nodes_from([('b1_proj', i) for i in range(n1)], bipartite=1)
    top_nodes = [('b1', i) for i in range(n1)] + [('b2_proj', i) for i in range(n2)]

    eps = 0
    nexts = dists.copy()
    while not nexts[0][2]:
        cur = nexts.pop(0)
        G.add_edge(cur[0], cur[1])


    matching = dict()
    n = n1 + n2
    while len(matching.keys()) < 2*n:
        u, v, eps = nexts.pop(0)
        G.add_edge(u, v)
        matching = nx.bipartite.maximum_matching(G, top_nodes)
    return eps


# NEVER USED
# Computes wheter bottleneck(b1,b2) is between down and up
# Returns S, I1, M, I2, U if smaller, inside I1, middle, inside I2 or greater
def bottleneck_is_between(b1, b2, I1, I2):

    # Overused scheme
    def fill_bipartite(bip, filler, limit):
        while filler[0][2] < limit:
            cur = filler.pop(0)
            bip.add_edge(cur[0], cur[1])

    n1, n2 = len(b1), len(b2)
    dists = barcode_distances(b1, b2)

    # Initializing Bipartite
    G = nx.Graph()
    G.add_nodes_from([('b1', i) for i in range(n1)], bipartite=0)
    G.add_nodes_from([('b2_proj', i) for i in range(n2)], bipartite=0)
    G.add_nodes_from([('b2', i) for i in range(n2)], bipartite=1)
    G.add_nodes_from([('b1_proj', i) for i in range(n1)], bipartite=1)
    top_nodes = [('b1', i) for i in range(n1)] + [('b2_proj', i) for i in range(n2)]

    n = n1 + n2
    nexts = dists.copy()
    fill_bipartite(G, nexts, I2[1])

    # Need to begin by greater case because it is by far the most frequent
    matching = nx.bipartite.maximum_matching(G, top_nodes)
    if len(matching) < 2 * n:
        return 'G'

    G.remove_edges_from(list(G.edges.keys()))
    nexts = dists.copy()
    fill_bipartite(G, nexts, I1[0])

    matching = nx.bipartite.maximum_matching(G, top_nodes)
    if len(matching) >= 2 * n:  # Should never be strictly
        return 'S'

    fill_bipartite(G, nexts, I1[1])
    matching = nx.bipartite.maximum_matching(G, top_nodes)
    if len(matching) >= 2 * n:  # Should never be strictly
        return 'I1'

    fill_bipartite(G, nexts, I2[0])
    matching = nx.bipartite.maximum_matching(G, top_nodes)
    if len(matching) >= 2 * n:  # Should never be strictly
        return 'M'

    return 'I2'
