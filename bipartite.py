# Draft of a bipartite maximum matching finder

# b1, b2_proj,
# b1_proj, b_2
def to_bipartite(b1, b2):
    b1_proj = []  # Projection of b1 points on the diagonal
    b2_proj = []  # Projection of b2 points on the diagonal
    for s, e in b1:
        b1_proj.append(((s+e)/2, (s+e)/2))
    for s, e in b2:
        b2_proj.append(((s+e)/2, (s+e)/2))

    N = len(b1) + len(b2)
    dists = []

    U = b1 + b2_proj
    V = b1_proj + b2
    # b1 and proj_b1
    for s, e in U:
        dists.append([])
        for s2, e2 in V:
            dists[-1].append(max(abs(s-s2), abs(e-e2)))


# Convention : an edge u,v is represented as u,v and never v,u
class Bipartite():
    # dists format : (u,v,dist)
    def __init__(self, dists, _sorted=False):
        self.order = dists
        if not _sorted:
            self.order.sort(key=lambda x: x[2])
        self.dists = dict()
        for u,v,d in self.order:
            if u in self.dists:
                self.dists[u][v] = d
            else:
                self.dists[u] = dict()
                self.dists[u][v] = d

    def iter_edges(self):
        for u in self.dists:
            for v in self.dists[u]:
                yield (u, v)

    # Returns the bipartie graph with edges of distance less than eps
    def inf_to(self, eps):
        new_order = []
        for x in self.order:
            if x < eps:
                new_order.append(x)
            else:
                break
        return Bipartite(new_order, True)

    # Easier to implement version, O(n^3)
    # Returns true and augment the path when possible, return false otherwise
    # Remark : there is no cycle in the graph
    def easy_augment(self, path, method="BFS"):
        in_path = dict()
        for u,v in path:
            if u in in_path:
                in_path[v].add(u)
            else:
                in_path[v] = set()
                in_path[v].add(u)
        not_in_path = dict()
        for u in self.dists:
            if u in in_path:
                not_in_path[u] = set(self.dists[u]).difference(in_path[u])
            else:
                not_in_path[u] = set(self.dists[u])
        entries = [x[0] for x in not_in_path if x[0] not in [y[0] for y in path]]  # Sale
        exits = [x[1] for x in path if x[1] not in [y[1] for y in not_in_path]]
        res = []
        nexts = [(e,True) for e in entries] # True if is in U
        cur = (nexts.pop(), True)  # True if is in U
        res.append(cur)  # (Tuples are not mutable)
        while nexts and (cur[1] or cur[0] not in exits):
            blocked = True
            neighbours = None
            if cur[1]:
                neighbours = not_in_path[u]
            else:
                neighbours =
            for v in not_in_path:
                if (cur[1] and u==cur[0]) or (not cur[1] and v==cur[0]):
                    blocked = False
                    if cur[1]:
                        cur = (v, not cur[1])
                    else:
                        cur = (u, not cur[1])
                    res.append(cur)
                    if method == "BFS":
                        nexts = nexts + [(x, not cur[1]) for x in self.dists[u].keys()]
                    else:
                        nexts = [(x, not cur[1]) for x in self.dists[u].keys()] + nexts
                    break
            if blocked:
                cur = res.pop()


    # Optimized version, O(n^2.5)
    def opt_augment(self, path):


    def find_maximum_matching(self):
        path = []  # TODO : init ?
        while self.easy_augment(path):
            pass
        return path


# Returns whether the bottleneck distance between b1 and b2 is less than epsilon
def bottleneck_smaller(b1, b2, eps):
    pass

# Comutes the bottleneck distance between b1 and b2
def bottleneck(b1, b2, eps=None)
    return 0.0
