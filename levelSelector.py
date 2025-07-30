import pygame
import sys
import os
import screen

pygame.init()

path = os.getcwd()
# 修改路径拼接方式，使用os.path.join并避免硬编码反斜杠
images_path = os.path.normpath(os.path.join(path, "images", "interface"))
font_path = os.path.normpath(os.path.join(path, "font"))     # 字体路径

# 字体文件路径使用os.path.join
screen_title_font = pygame.font.Font(os.path.join(font_path, "方正少儿GBK简体.ttf"), 36)
screen_scenario_font = pygame.font.Font(os.path.join(font_path, "方正少儿GBK简体.ttf"), 22)
screen_level_font = pygame.font.Font(os.path.join(font_path, "方正卡通简体.TTF"), 19)
screen_back_font = pygame.font.Font(os.path.join(font_path, "华康流行简体-细.ttc"), 15)
bg = pygame.image.load(os.path.join(images_path, "Challenge_Background.jpg")).convert()
back_image = pygame.image.load(os.path.join(path, "images", "Almanac_CloseButton.png"))
back_image_on = pygame.image.load(os.path.join(path, "images", "Almanac_CloseButton1.png"))

'''文字转图片'''
title = screen_title_font.render("冒险模式", True, "black")
grass = screen_scenario_font.render("草地", True, "green")
pool = screen_scenario_font.render("泳池", True, "green")
day = screen_scenario_font.render("白天", True, "green")
night = screen_scenario_font.render("夜晚", True, "green")
back = screen_back_font.render("返回", True, [10, 0, 125])
nums = ('一', '二', '三', '四', '五', '六', '七', '八', '九', '十')
running: bool = True


def back_cmd():
    screen.change_name('inter')
    global running
    running = False


# 制作按钮
back_rect = back.get_rect()
back_rect.left, back_rect.top = 723, 567
back_button = screen.GameButton([back_rect], back_image, back_image_on, (700, 565), command=back_cmd)
levels_image: list = []
grass_day_levels_button: list = []
for num in nums:
    levels_image.append(
        screen_level_font.render(
            '第' + num + '关', True, 'black'))

pos = (260, 125)
i = 1
for image in levels_image:
    grass_day_levels_button.append(
        screen.GameButton(
            [image.get_rect()], button_image1=image, position=pos))
    if i % 5 == 0:
        pos = pos[0] - 5*80, pos[1] + 34
    pos = pos[0] + 80, pos[1]
    i = i + 1

i = 1
pos = 260, 210
grass_night_levels_button: list = []
for image in levels_image:
    grass_night_levels_button.append(
        screen.GameButton(
            [image.get_rect()], button_image1=image, position=pos))
    if i % 5 == 0:
        pos = pos[0] - 5*80, pos[1] + 34
    pos = pos[0] + 80, pos[1]
    i = i + 1

i = 1
pos = 260, 295
pool_day_levels_button: list = []
for image in levels_image:
    pool_day_levels_button.append(screen.GameButton(
        [image.get_rect()], button_image1=image, position=pos))
    if i % 5 == 0:
        pos = pos[0] - 5*80, pos[1] + 34
    pos = pos[0] + 80, pos[1]
    i = i + 1

pos = 260, 380
pool_night_levels_button = screen.GameButton(
    levels_image[0].get_rect, button_image1=levels_image[0], position=pos)


def selector():
    global running
    running = True
    back_desk = 723, 567

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                # 鼠标移动事件处理
            back_button.is_on(event)
            # 鼠标点击事件处理
            back_button.isdown(event)
            if back_button.button_down == 1:
                back_desk = 723, 569
            else:
                back_desk = 723, 567

        if running is True:
            screen.screen1.blit(bg, (0, 0))
            screen.screen1.blit(title, (330, 27))
            screen.screen1.blit(day, (65, 135))
            screen.screen1.blit(grass, (65, 160))
            screen.screen1.blit(night, (65, 220))
            screen.screen1.blit(grass, (65, 245))
            screen.screen1.blit(day, (65, 305))
            screen.screen1.blit(pool, (65, 330))
            screen.screen1.blit(night, (65, 390))
            screen.screen1.blit(pool, (65, 415))
            for l in grass_day_levels_button:
                l.draw()
            for l in grass_night_levels_button:
                l.draw()
            for l in pool_day_levels_button:
                l.draw()
            pool_night_levels_button.draw()
            back_button.draw()
            screen.screen1.blit(back, back_desk)
            pygame.display.flip()


if __name__ == '__main__':
    selector()
