import numpy as np
from graph import Graph


orientations = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', '']


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


def opposite_orientation(o):
    if o == 'N':
        return 'S'
    elif o == 'S':
        return 'N'
    elif o == 'E':
        return 'W'
    elif o == 'W':
        return 'E'
    elif o == 'SE':
        return 'NW'
    elif o == 'NW':
        return 'SE'
    elif o == 'SW':
        return 'NE'
    elif o == 'NE':
        return 'SW'
    else:
        return ''


# Returns whether s1 and s2 are opposite speed
def opposite_speed(direction_dict1, direction_dict2):
    for direction in orientations:
        if len(direction_dict1[direction]) != len(direction_dict2[opposite_orientation(direction)]):
            return False
    return True


# Returns if going from p1 with orientation o gives p2
def is_aligned(o, p1, p2, eps):
    if o == 'N':
        return abs(p1[0] - p2[0]) < eps and p1[1] + eps < p2[1]
    elif o == 'S':
        return abs(p1[0] - p2[0]) < eps and p1[1] - eps > p2[1]
    elif o == 'E':
        return abs(p1[1] - p2[1]) < eps and p1[0] + eps < p2[0]
    elif o == 'W':
        return abs(p1[1] - p2[1]) < eps and p1[0] - eps > p2[0]
    elif o == 'NE':
        return abs((p2[0] - p1[0]) - (p2[1]-p1[1])) < eps and p2[0] > p1[0] + eps
    elif o == 'SW':
        return abs((p2[0] - p1[0]) - (p2[1]-p1[1])) < eps and p2[0] < p1[0] - eps
    elif o == 'NW':
        return abs((p2[0] - p1[0]) + (p2[1]-p1[1])) < eps and p2[0] < p1[0] - eps
    elif o == 'SE':
        return abs((p2[0] - p1[0]) + (p2[1]-p1[1])) < eps and p2[0] > p1[0] + eps
    else:
        assert o == ''
        return abs(p1[0] - p2[0]) < eps and abs(p1[1] - p2[1]) < eps


def orientation_to_speed(o):
    res = [0, 0]
    for c in o:
        if c == 'N':
            res[1] += 1
        elif c == 'E':
            res[0] += 1
        elif c == 'S':
            res[1] -= 1
        elif c == 'W':
            res[0] -= 1
    return tuple(res)


def inf_dist(p, q):
    return max(abs(p[0]-q[0]), abs(p[1] - q[1]))