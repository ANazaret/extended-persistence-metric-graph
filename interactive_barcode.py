import numpy as np
import pygame

from pygame.locals import *
from config import *


class InteractiveBarcode:
    def __init__(self, window):
        self.window = window
        self.origin = np.array([WINDOW_SIZE + (WINDOW_SIZE - BARCODE_SIZE) / 2, (WINDOW_SIZE - BARCODE_SIZE) / 2])
        self.window_size = WINDOW_SIZE
        self.barcode_size = BARCODE_SIZE
        self.intervals = []

        self.reverse_barcode = False
        self.reverse_mapping = False
        self.reeb = None

    def handle_event(self, event):
        if event.type == KEYDOWN:
            if event.key == K_r:
                self.reverse_barcode ^= True

    def change_coordinates(self, x, y):
        return [int(x / 2 + self.origin[0]), int(self.origin[1] + self.barcode_size - y / 2)]

    def draw(self):
        pygame.draw.line(self.window, BLACK,
                         self.origin,
                         self.origin + [0, self.barcode_size])
        pygame.draw.line(self.window, BLACK,
                         self.origin + [0, self.barcode_size],
                         self.origin + [self.barcode_size, self.barcode_size])
        pygame.draw.line(self.window, BLACK,
                         self.origin + [self.barcode_size, self.barcode_size],
                         self.origin + [self.barcode_size, 0])
        pygame.draw.line(self.window, BLACK,
                         self.origin + [self.barcode_size, 0],
                         self.origin)
        pygame.draw.line(self.window, BLACK,
                         self.origin + [self.barcode_size, 0],
                         self.origin + [0, self.barcode_size])

        for d, s, e, t in self.intervals:
            pygame.draw.circle(self.window, COLORS_DIM_TYPE[d][t.value],
                               self.change_coordinates(s, e), 5)
            if self.reverse_barcode and (d, s, e, t) in self.reverse_mapping:
                birth, death = self.reverse_mapping[(d, s, e, t)]
                pygame.draw.line(self.window, GREEN_B,
                                 self.change_coordinates(s, e),
                                 self.reeb.node_positions[birth])
                pygame.draw.line(self.window, RED_B,
                                 self.change_coordinates(s, e),
                                 self.reeb.node_positions[death])
