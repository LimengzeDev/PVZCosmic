import pygame
import sys
import os
import screen
import account


pygame.init ()
pygame.mixer.init ()
path = os.getcwd()
images_path = os.path.join(path, "images\\")  # image

current_dir = os.getcwd()  # 例如: C:\Users\...\PythonProject\str

# 正确拼接路径
music_path = os.path.join(current_dir, "music\\", "")
pygame.mixer.music.load (music_path+'Faster.mp3')


#下载图片
#以及获得按钮图片的位置矩形
surface = pygame.image.load (images_path + "Surface.jpg").convert()

adventure = pygame.image.load (images_path + 'SelectorScreenAdventure.png').convert_alpha()
adventure_start = pygame.image.load (images_path + 'SelectorScreenStartAdventure.png').convert_alpha()
adventure_on = pygame.image.load (images_path + 'SelectorScreenAdventure1.png').convert_alpha()
adventure_start_on = pygame.image.load (images_path + 'SelectorScreenStartAdventure1.png').convert_alpha()

challenges = pygame.image.load (images_path + 'SelectorScreenChallenges.png').convert_alpha()
challenges_rect = challenges.get_rect ()

survival = pygame.image.load (images_path + 'SelectorScreenSurvival.png').convert_alpha()
survival_rect = survival.get_rect ()

WoodSign1 = pygame.image.load (images_path + 'SelectorScreen_WoodSign1_32.png').convert_alpha()
WoodSign2_on = pygame.image.load (images_path + 'SelectorScreen_WoodSign2_32_1.png').convert_alpha()
WoodSign2 = pygame.image.load (images_path + 'SelectorScreen_WoodSign2_32.png').convert_alpha()
WoodSign3 = pygame.image.load (images_path + 'SelectorScreen_WoodSign3_32.png').convert_alpha()
wood_sign2_rect = WoodSign2.get_rect ()
wood_sign2_rect.left, wood_sign2_rect.top = 20, 140
wood_sign2_rect.width, wood_sign2_rect.height = wood_sign2_rect.width - 20, wood_sign2_rect.height - 20

survival_shadow = pygame.image.load (images_path + 'SelectorScreen_Shadow_Survival.png').convert_alpha()
adventure_shadow = pygame.image.load (images_path + 'SelectorScreen_Shadow_Adventure.png').convert_alpha()
challenges_shadow = pygame.image.load (images_path + 'SelectorScreen_Shadow_Challenge.png').convert_alpha()


def inter ():
    pygame.mixer.music.play (-1)  #播放背景音乐
    if account.counter == 1 :
        adv = adventure_start
        adv_on = adventure_start_on
    else:
        adv = adventure
        adv_on = adventure_on
        #默认显示
    # noinspection PyStatementEffect
    adv_rect1 = adv.get_rect ()
    adv_rect2 = adv.get_rect ()
    adv_rect1.left, adv_rect1.top = 478, 85
    adv_rect1.width, adv_rect1.height = adv_rect1.width - 9, adv_rect1.height - 70
    adv_rect2.left, adv_rect2.top = 478 + 205, 85 + 74
    adv_rect2.width, adv_rect2.height = 117, 23
    adv_button = screen.GameButton ([adv_rect1,adv_rect2], adv, adv_on, (475,53), (-2,0), adv_cmd)
    wood2_button = screen.GameButton ([wood_sign2_rect], WoodSign2, WoodSign2_on, (10,138), (0,1))
    
    while True:
        for event in pygame.event.get ():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit ()
            #鼠标移动事件处理
            adv_button.is_on (event)
            wood2_button.is_on (event)
            #鼠标点击事件处理
            adv_button.isdown(event)
            wood2_button.isdown(event)
        #绘制图片
        screen.screen1.blit (surface, (0, 0))
        screen.screen1.blit (WoodSign1, (10, 0))
        wood2_button.drow()
        screen.screen1.blit (WoodSign3, (10, 200))
        screen.screen1.blit (adventure_shadow, (466, 54))
        screen.screen1.blit (survival_shadow,  (476, 166))
        screen.screen1.blit (challenges_shadow, (481, 255))
        adv_button.drow()
        screen.screen1.blit (survival, (475, 161))
        screen.screen1.blit (challenges, (480, 251))
        pygame.display.flip ()


def adv_cmd ():
    screen.change_name('levelSelector')
    print('fuck')