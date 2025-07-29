import pygame
import sys
import os
import screen

pygame.init()

path = os.getcwd()
images_path = os.path.join(path, "images\\interface\\")
font_path = os.path.join(path, "font\\TTF TTC(字体安装)\\")     # 字体路径
screen_title_font = pygame.font.Font(font_path + "方正少儿GBK简体.ttf", 36)
screen_scenario_font = pygame.font.Font(font_path + "方正少儿GBK简体.ttf", 22)
screen_level_font = pygame.font.Font(font_path + "方正卡通简体.TTF", 19)
bg = pygame.image.load(images_path + "Challenge_Background.jpg").convert()
'''文字转图片'''
title = screen_title_font.render("冒险模式", True, "black")
grass = screen_scenario_font.render("草地", True, "green")
pool = screen_scenario_font.render("泳池", True, "green")
day = screen_scenario_font.render("白天", True, "green")
night = screen_scenario_font.render("夜晚", True, "green")
nums = ('一', '二', '三', '四', '五', '六', '七', '八', '九', '十')
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
running: bool = True


def selector():
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
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
        pygame.display.flip()


if __name__ == '__main__':
    selector()
