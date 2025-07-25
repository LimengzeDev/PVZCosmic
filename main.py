from interface import inter
import levelSelector
import screen
import pygame

pygame.init()
pygame.mixer.init()
running: bool = True

print(inter.__name__)

ID = [inter]
while running:
    for name in ID:
        if name.__name__ == 'inter':
            name()
            break
    else:
        inter()
