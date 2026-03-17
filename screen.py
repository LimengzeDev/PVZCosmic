import pygame
import subprocess
import time
name = 'inter'


def change_name(new):
    global name
    name = str(new)


pygame.init()

size = (900, 600)     # 窗口大小
screen1 = pygame.display.set_mode(size)
pygame.display.set_caption("PlantsVsZombies")


class GameButton:
    """游戏按钮类"""
    
    def __init__(self, button_rect: list, button_image1: pygame.Surface = None,
                 button_image2: pygame.Surface = None, position=(0, 0), modify=(0, 0), command=None, file=None):
        """
        :param position: 图片左上角坐标
        :param modify: 绘制另一张图时,为使图片位置不变,对 position 的修正量
        :param button_image1: 为按钮不同状态下的图片
        :param button_image2: 同 button_image1,image1 为默认图片赋值给 image
        :param button_rect: 为按钮的位置矩形，可以有多个,用列表的形式上传参数
        :param command: 为按钮按下时执行的命令
        :param file: 为要打开的文件
        """
        self.button_image1 = button_image1
        self.button_image2 = button_image2
        self.image = button_image1
        self.button_rect = button_rect
        self.position = position
        self.pos = position
        self.modify = modify
        self.button_down = 0        #按钮是否按下的状态,按下时为 1,未按下时为 0
        self.command = command
        self.file_to_open = file  # 存储要打开的文件路径

    def is_on(self, event):
        """检测鼠标是否在按钮上"""
        if event.type == pygame.MOUSEMOTION:
            for rect in self.button_rect:
                if rect.collidepoint(event.pos):
                    self.image = self.button_image2  # 如果鼠标在按钮上绘制另一张图片
                    break
            else:
                if self.button_down == 0:
                    self.image = self.button_image1         # 否则绘制原图片
    
    def is_click(self, event):
        """检测按钮是否按下"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            for rect in self.button_rect:
                if rect.collidepoint(event.pos) and event.button == 1:
                    self.image = self.button_image2
                    self.button_down = 1
                    # 按下时图片向下移2像素
                    self.pos = self.position[0] + self.modify[0], self.position[1] + self.modify[1] + 2
                    break
        if event.type == pygame.MOUSEBUTTONUP:  # 在按钮内松开时执行命令
            if event.button == 1 and self.button_down == 1:
                self.image = self.button_image1
                self.button_down = 0
                for rect in self.button_rect:
                    if rect.collidepoint(event.pos):
                        if self.command is not None:
                            self.command()
                        if self.file_to_open is not None:
                            self.open_file()
                        break

    def open_file(self):
        """打开指定的Python文件"""
        try:
            # 使用subprocess运行指定的Python文件
            subprocess.Popen(['python', self.file_to_open])
            """
            或者使用os.system (根据你的系统选择合适的方式)
            os.system(f 'python {self.file_to_open}')
            """
        except Exception as e:
            print(f"无法启动关卡程序: {self.file_to_open}")
            print(f"错误信息: {e}")

    def draw(self):
        """绘制按钮"""
        if self.button_down == 0:
            if self.image == self.button_image1:
                self.pos = self.position
            elif self.image == self.button_image2:
                self.pos = self.position[0] + self.modify[0], self.position[1] + self.modify[1]

        if self.image is not None:
            screen1.blit(self.image, self.pos)
        elif self.button_image1 is not None:
            screen1.blit(self.button_image1, self.pos)
        elif self.button_image2 is not None:
            screen1.blit(self.button_image2, self.pos)
        else:
            pass


class GameTimer:
    """倒计时器类"""
    def __init__(self, duration):
        """
        初始化计时器
        :param duration: 倒计时秒数
        """
        self.duration = duration
        self.start_time = None
        self.active = False

    def start(self, duration=None):
        """启动计时器"""
        if duration is not None:
            self.duration = duration
        self.start_time = time.time()
        self.active = True

    def is_finished(self):
        """
        查询计时器是否结束
        时间到返回True,否则返回False
        """
        if not self.active or self.start_time is None:
            return False
        elif time.time()-self.start_time >= self.duration:
            self.active = False
            return True

    def time_left(self):
        """返回剩余时间(秒),没开始返回None"""
        if self.start_time is None:
            return None
        else:
            left = self.duration - (time.time() - self.start_time)
            return max(0, left)
