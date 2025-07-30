import pygame
import subprocess
import os
name='interface'
def change_name(new):
    global name
    name=str(new)
size = (900,600)     #窗口大小
screen1 = pygame.display.set_mode(size)
pygame.display.set_caption("PlantsVsZombies")

class GameButton:   #定义按钮类

    """
    button_image1和button_image2为按钮不同状态下的图片
    其中button_image1为默认显示的图片
    image为要绘制的图片
    button_rect为按钮的位置矩形，可以有多个，
    用列表的形式上传参数
    button_down为按钮是否按下的状态
    按下时为 1
    按下时为 0
    """
    
    def __init__ (self, button_rect, button_image1, button_image2=None):
        self.button_image1 = button_image1
        self.button_image2 = button_image2
        self.image = button_image1
        self.button_rect = button_rect
        self.button_down = 0
        self.file_to_open = "levelManager.py"  # 存储要打开的文件路径


    def is_on (self,event):
        if event.type == pygame.MOUSEMOTION:        #检测鼠标是否在按钮上
            for rect in self.button_rect:
                if rect.collidepoint (event.pos):
                    self.image = self.button_image2  #如果在绘制另一张图片
                    break
            else:
                self.image = self.button_image1         #否则绘制原图片
    
    def isdown (self, event, button_down=None):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for rect in self.button_rect:
                if rect.collidepoint (event.pos) and button_down == 0:
                    self.button_down = 1
                    self.open_file()
        else:
            self.button_down = 0
    def open_file(self):
        """打开指定的Python文件"""
        try:
            # 使用subprocess运行指定的Python文件
            subprocess.Popen(['python', self.file_to_open])
            # 或者使用os.system (根据你的系统选择合适的方式)
            # os.system(f'python {self.file_to_open}')
        except Exception as e:
            print(f"无法启动关卡程序: {self.file_to_open}")
            print(f"错误信息: {e}")
            