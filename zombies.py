import pygame


class Zombie(pygame.sprite.Sprite):
    def __init__(self, images: list, line=1) -> None:
        super().__init__()
        self.hp = 270.0
        self.speed = 0.6
        self.line = line
        self.images = images
        self.image = images[0]
        self.slow = False
        self.lost_arm = False
        self.lost_head = False

    def update(self) -> None: ...
    def draw(self) -> None: ...

