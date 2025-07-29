import screen
from interface import inter
from levelSelector import selector
import pygame

pygame.init()
pygame.mixer.init()
running: bool = True

ID = [inter, selector]
while running:
    for name in ID:
        if name.__name__ == screen.name:
            name()
            break
    else:
        inter()
