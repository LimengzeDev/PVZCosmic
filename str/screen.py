import pygame

name='interface'
def change_name(new):
    global name
    name=str(new)
size = (900,600)     #窗口大小
screen1 = pygame.display.set_mode(size)
pygame.display.set_caption("PlantsVsZombies")

class GameButton:
    def __init__(self,button_image1,button_image2=None,image_rect=()):
        self.button_image1 = button_image1
        self.button_image2 = button_image2
        self.image=button_image1
        self.image_rect = image_rect
    def down(self,event,style,new_name):
        if style == 'down_up':
            if event.type == pygame.MOUSEBUTTONDOWN:
                for rect in self.image_rect:
                    if rect.collidepoint(event.pos):
                        self.image = self.button_image2
            elif event.type == pygame.MOUSEBUTTONUP:
                self.image = self.button_image1
                change_name(new_name)