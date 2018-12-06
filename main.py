import pygame
from pygame.locals import *

from interactive_graph import InteractiveGraph

window_size = 800

pygame.init()
window = pygame.display.set_mode([window_size*2, window_size])
interactive = InteractiveGraph(window)


while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()

        if event.type in [MOUSEBUTTONUP, MOUSEMOTION, MOUSEBUTTONDOWN]:
            if event.pos[0] < window_size:
                interactive.handle_event(event)

    window.fill((255, 255, 255))
    pygame.draw.line(window, (0,0,0), [window_size,0], [window_size,window_size])
    interactive.draw()
    pygame.display.update()
    pygame.time.wait(15)

