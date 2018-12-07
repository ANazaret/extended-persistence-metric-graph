import pygame
from pygame.locals import *

from config import *
from interactive_barcode import InteractiveBarcode
from interactive_graph import InteractiveGraph

pygame.init()
window = pygame.display.set_mode([WINDOW_SIZE * 2, WINDOW_SIZE])
interactive_graph = InteractiveGraph(window)
interactive_barcode = InteractiveBarcode(window)
interactive_graph.bind_interactive_barcode(interactive_barcode)

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()

        if event.type in [MOUSEBUTTONUP, MOUSEMOTION, MOUSEBUTTONDOWN]:
            if event.pos[0] < WINDOW_SIZE:
                interactive_graph.handle_event(event)

    window.fill((255, 255, 255))
    pygame.draw.line(window, (0, 0, 0), [WINDOW_SIZE, 0], [WINDOW_SIZE, WINDOW_SIZE])
    interactive_graph.draw()
    interactive_barcode.draw()
    pygame.display.update()
    pygame.time.wait(15)
