import numpy as np
import pygame

from config import *


class InteractiveBarcode:
    def __init__(self, window):
        self.window = window
        self.origin = np.array([WINDOW_SIZE + (WINDOW_SIZE - BARCODE_SIZE) / 2, (WINDOW_SIZE - BARCODE_SIZE) / 2])
        self.window_size = WINDOW_SIZE
        self.barcode_size = BARCODE_SIZE
        self.intervals = []

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

        for d, s, e in self.intervals:
            pygame.draw.circle(self.window, COLORS_DIM[d],
                               [int(s / 2 + self.origin[0]), int(self.origin[1] + self.barcode_size - e / 2)], 5)
