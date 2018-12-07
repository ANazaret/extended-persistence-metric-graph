import numpy as np
import pygame
from pygame.locals import *

from config import *
from graph import Graph
from simplicial_complex import SimplicialComplex


class InteractiveGraph:
    def __init__(self, window):
        self.window = window
        self.graph = Graph()
        self.node_positions = dict()
        self.edge_normals = dict()

        self.focus_node = None
        self.edge_mode = None

        self.base_point = None

        self.interactive_barcode = None

    def bind_interactive_barcode(self, interactive_barcode):
        self.interactive_barcode = interactive_barcode

    def draw(self):
        if self.edge_mode is not None:
            pygame.draw.line(self.window, BLACK, self.node_positions[self.edge_mode], pygame.mouse.get_pos())

        for u, v, _ in self.graph.iter_edges():
            edge_color = NODE_COLOR_FOCUS if (self.base_point is not None and
                                              self.base_point[1] and
                                              u in self.base_point[2][:2] and
                                              v in self.base_point[2][:2]) else BLACK
            pygame.draw.line(self.window, edge_color, self.node_positions[u], self.node_positions[v])

        for n in self.node_positions:
            node_color = NODE_COLOR_FOCUS if self.focus_node == n else NODE_COLOR
            pygame.draw.circle(self.window, node_color, self.node_positions[n], NODE_RADIUS)
            pygame.draw.circle(self.window, BLACK, self.node_positions[n], NODE_RADIUS, 1)

        if self.base_point is not None:
            pygame.draw.circle(self.window, NODE_COLOR_BASE, self.base_point[0], int(NODE_RADIUS * 0.8))
            pygame.draw.circle(self.window, BLACK, self.base_point[0], int(NODE_RADIUS * 0.8), 1)

        if not self.graph.is_connected:
            text = str('Graph is not connected (or less than 2 nodes)')
            font = pygame.font.Font('freesansbold.ttf', 10)
            text = font.render(text, True, (255, 0, 0))
            self.window.blit(text, (0, 0))

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            over_node = self.find_node(*event.pos, NODE_RADIUS ** 2)
            if event.button == 1:
                # If not on a node (and far at least by 2*radius for non-overlapping)
                # Add a node
                if self.find_node(*event.pos, (2 * NODE_RADIUS) ** 2) is None:
                    self.add_node(*event.pos)
                else:
                    self.edge_mode = over_node

        if event.type == MOUSEBUTTONUP:
            over_node = self.find_node(*event.pos, NODE_RADIUS ** 2)
            if event.button == 1:
                if self.edge_mode is not None and over_node is not None and self.edge_mode != over_node:
                    self.add_edge(self.edge_mode, over_node)
                self.edge_mode = None

        if event.type == MOUSEMOTION:
            over_node = self.find_node(*event.pos, NODE_RADIUS ** 2)
            self.focus_node = over_node

            if pygame.mouse.get_pressed()[2]:
                self.update_base_point(*event.pos)

    def find_node(self, x, y, distance):
        for n, (nx, ny) in self.node_positions.items():
            if (nx - x) ** 2 + (ny - y) ** 2 <= distance:
                return n
        return None

    def update_base_point(self, x, y):
        if not self.graph.is_connected:
            return
        base_point = self.find_closest_point_on_edge(x, y)
        if base_point is not None:
            if type(base_point) == int:
                self.base_point = (self.node_positions[base_point], False, base_point)
            else:
                u, v, alpha = base_point
                position = (1 - alpha) * self.node_positions[u] + alpha * self.node_positions[v]
                self.base_point = (position.astype(int), True, (u, v, alpha))

        self.update_barcode()

    def update_barcode(self):
        if self.base_point is None:
            return

        if self.base_point[1]:
            u, v, alpha = self.base_point[2]
            graph, base_point = self.graph.copy_and_insert_base_point(u, v, alpha)
        else:
            graph, base_point = self.graph, self.base_point[2]

        filtration = SimplicialComplex.from_graph_extended(graph, base_point)
        self.interactive_barcode.intervals = filtration.get_barcode()
        print(self.interactive_barcode.intervals)

    def find_closest_point_on_edge(self, x, y):
        min_distance = 100000
        x_ = x
        y_ = y
        # Check edges
        min_point = None
        for (u, v), normal in self.edge_normals.items():
            # Project to the line
            x = x_ - self.node_positions[u][0]
            y = y_ - self.node_positions[u][1]
            d = abs(normal.dot([x, y]))
            if d < min_distance:
                # Check projection belongs to the segment
                alpha = - normal[1] * x + normal[0] * y
                if 0 <= alpha <= self.graph[u][v]:
                    min_distance = d
                    min_point = (u, v, alpha / self.graph[u][v])

        # Check vertices
        for n, (nx, ny) in self.node_positions.items():
            d2 = (nx - x_) ** 2 + (ny - y_) ** 2
            if d2 <= min_distance ** 2:
                min_distance = d2 ** 0.5
                min_point = n

        return min_point

    def add_node(self, x, y):
        node = self.graph.number_of_nodes
        self.graph.add_node(node)
        self.node_positions[node] = np.array([x, y])

    def add_edge(self, u, v):
        if u > v:
            u, v = v, u
        ux, uy = self.node_positions[u]
        vx, vy = self.node_positions[v]
        w = ((ux - vx) ** 2 + (uy - vy) ** 2) ** 0.5
        self.graph.add_edge(u, v, w)

        self.edge_normals[(u, v)] = np.array([vy - uy, ux - vx]) / w
