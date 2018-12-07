import argparse
import os

import pygame
from pygame.locals import *

from config import *
from interactive_barcode import InteractiveBarcode
from interactive_graph import InteractiveGraph

parser = argparse.ArgumentParser()
parser.add_argument('-g', '--graphfile',
                    help='load a graph from the file GRAPHFILE, and will save changes to this same file')
args = parser.parse_args()

pygame.init()
window = pygame.display.set_mode([WINDOW_SIZE * 2, WINDOW_SIZE])

if args.graphfile:
    if os.path.exists(args.graphfile):
        interactive_graph = InteractiveGraph.load_from_file(window, args.graphfile)
    else:
        interactive_graph = InteractiveGraph(window, args.graphfile)
else:
    interactive_graph = InteractiveGraph(window)

interactive_barcode = InteractiveBarcode(window)
interactive_graph.bind_interactive_barcode(interactive_barcode)

trace_activated = False

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()

        if event.type in [MOUSEBUTTONUP, MOUSEMOTION, MOUSEBUTTONDOWN]:
            if event.pos[0] < WINDOW_SIZE:
                interactive_graph.handle_event(event)

        interactive_barcode.handle_event(event)
        if event.type == KEYDOWN:
            if event.key == K_s:
                interactive_graph.write()
            if event.key == K_t:
                trace_activated ^= True

    if trace_activated:
        pygame.draw.rect(window, (255, 255, 255), Rect([0, 0], [WINDOW_SIZE, WINDOW_SIZE]))
    else:
        window.fill((255, 255, 255))

    pygame.draw.line(window, (0, 0, 0), [WINDOW_SIZE, 0], [WINDOW_SIZE, WINDOW_SIZE])
    interactive_graph.draw()
    interactive_barcode.draw()
    pygame.display.update()
    pygame.time.wait(15)
