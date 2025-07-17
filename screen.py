import pygame

name='interface'
def change_name(new):
    global name
    name=str(new)
size = (900,600)     #窗口大小
screen1 = pygame.display.set_mode(size)
pygame.display.set_caption("PlantsVsZombies")

class GameButton:   #定义按钮类
    
    '''
    button_image1和button_image2为按钮不同状态下的图片
    其中button_image1为默认显示的图片
    iamge为要绘制的图片
    button_rect为按钮的位置矩形，可以有多个，
    用元组的形式上传参数
    button_down为按钮是否按下的状态
    position为按钮图片绘制时矩形左上角的坐标
    按下时为 1
    为按下时为 0
    '''
    
    def __init__ (self,button_image1,button_image2 = None,button_rect = (),position = (0,0)):
        self.button_image1 = button_image1
        self.button_image2 = button_image2
        self.image = button_image1
        self.image_rect = button_rect
        self.position = position
        self.button_down = 0
        
    def is_on (self,event):
        if event.type == pygame.MOUSEMOTION:        #检测鼠标是否在按钮上
            for rect in self.image_rect:
                if rect.collidepoint (event.pos):
                    self.image = self.button_image2  #如果在绘制另一张图片
        else:
            self.image = self.button_image1         #否则绘制原图片
    
    def isdown (self,event):
        if event.type == pygame.MOUSEBUTTONDON:
            for rect in self.image_rect:
                if rect.collidepoint (event.pos) and button_down == 0:
                    self.button_down = 1
                else:
                    self.button_down = 0
