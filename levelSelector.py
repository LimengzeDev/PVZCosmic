import pygame
import os
import screen

pygame.init()

path = os.getcwd()
images_path = os.path.join (path, "images\\interface\\")
font_path = os.path.join (path, "font\\TTF TTC(字体安装)\\")
screen_tetel_font = pygame.font.Font(font_path+"方正少儿GBK简体.ttf", 36)
screen_scenario_font = pygame.font.Font(font_path+"方正少儿GBK简体.ttf",22)
bg =pygame.image.load(images_path + "Challenge_Background.jpg").convert()
tetel = screen_tetel_font.render("冒险模式", True, "black")
grass = screen_scenario_font.render("草地", True, "green")
pool = screen_scenario_font.render("泳池", True, "green")
day = screen_scenario_font.render("白天", True, "green")
night = screen_scenario_font.render("夜晚", True, "green")

if __name__ == '__main__':
    selector_size = (900, 600)
    selector_screen= pygame.display.set_mode(selector_size)
    pygame.display.set_caption("levelSelector")
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        selector_screen.blit (bg, (0, 0))
        selector_screen.blit(tetel, (330,27))
        selector_screen.blit(day, (65, 135))
        selector_screen.blit(grass, (65, 160))
        selector_screen.blit(night, (65, 220))
        selector_screen.blit(grass, (65, 245))
        selector_screen.blit(day, (65,305))
        selector_screen.blit(pool, (65, 330))
        selector_screen.blit(night, (65, 390))
        selector_screen.blit(pool, (65, 415))
        pygame.display.flip()