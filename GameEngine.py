import json
import pygame
import sys
from pathlib import Path
from pygame.locals import *
from plants import all_plants_animations

base_dir = Path(__file__).parent


class GameEngine:
    def __init__(self, levels_folder="levels", data_folder="data"):
        """
        整个窗口: 900*600
        草坪左上角点坐标: (145, 80)
        草坪右下角坐标: (875, 575)
        方格长: 81
        方格宽: 99
        """
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((900, 600))
        pygame.display.set_caption("Plants vs Zombies")
        self.clock = pygame.time.Clock()

        self.base_dir = Path(__file__).parent
        self.levels_folder = self.base_dir / levels_folder
        self.data_folder = self.base_dir / data_folder

        self.plants_data = self.load_data_file("plants.json")
        self.zombies_data = self.load_data_file("zombies.json")
        self.loaded_levels = self.load_all_levels()

        self.current_level = None
        self.W = 900
        self.H = 600
        self.C = 9
        self.LawnMowerX = 70
        self.SunNum = 50
        self.Chose = 0
        self.ChoseCard = ""
        self.MPID = ""
        self.cards = pygame.sprite.Group()
        self.ArSun = []
        self.Plants = pygame.sprite.OrderedUpdates()
        self.Zombies = {}
        self.DraggingCard = None
        self.DraggingImage = None
        self.DraggingPos = (0, 0)
        self.Grids = [[Grid(j, i) for i in range(9)] for j in range(5)]

        self.font = pygame.font.SysFont('Arial', 16)
        self.big_font = pygame.font.SysFont('Arial', 24)
        self.last_time = pygame.time.get_ticks()
        self.card_gray_images = {}
        self.BulletGroup = pygame.sprite.Group()
        self.last_bullet_time = pygame.time.get_ticks()
        self.last_update_time = pygame.time.get_ticks()


    def load_data_file(self, filename):
        file_path = self.data_folder / filename
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load {filename}: {str(e)}")
            return {}

    def load_all_levels(self):
        levels = {}
        for level_file in self.levels_folder.glob("*.json"):
            level_id = level_file.stem.split("_")[-1]
            try:
                with open(level_file, "r") as f:
                    levels[level_id] = json.load(f)
            except Exception as e:
                print(f"Failed to load level {level_file}: {str(e)}")
        return levels

    def load_level(self, level_id):
        self.current_level = self.loaded_levels.get(str(level_id))
        if self.current_level:
            self.init_level()
            return True
        return False

    def init_level(self):
        self.PName = self.current_level.get("PName", [])
        self.ZName = self.current_level.get("ZName", [])
        self.LevelName = self.current_level.get("LevelName", "Level")
        self.SunNum = self.current_level.get("SunNum", 50)

        self.init_plant_cards()

        bg_path = self.current_level.get("backgroundImage", "images/interface/background1.jpg")
        sb_path = base_dir / "images/interface/SeedBank.png"
        try:
            self.background = pygame.image.load(str(self.base_dir / bg_path))
            self.seedband = pygame.image.load(str(sb_path))
        except Exception as e:
            print(f"Failed to load background {bg_path}: {str(e)}")
            self.background = pygame.Surface((880, 600))
            self.background.fill((100, 200, 100))

    def init_plant_cards(self):
        for i, plant_type in enumerate(self.PName):
            card = Card(self, plant_type,10, 80 + i * 70)
            self.cards.add(card)    # type: ignore

    def create_plant(self, plant_type, x, y):
        """创建植物，添加攻击相关属性"""
        try:
            from plants import Plant
            plant:Plant = Plant(self, plant_type, x, y)

            return plant
        except Exception as e:
            print(f"Failed to create plant {plant_type}: {str(e)}")
            return None

    def update_bullets(self):
        """更新所有子弹状态"""
        self.BulletGroup.update()

    def update(self):
        self.last_update_time = pygame.time.get_ticks()

        # 植物更新
        self.Plants.update()

        # 格子更新
        for line in self.Grids:
            for grid in line:
                grid.update()

        # 卡片更新
        self.cards.update()
        
        # 子弹更新
        self.update_bullets()

        # 僵尸更新 & 攻击 & 清理
        for zombie_id, zombie in list(self.Zombies.items()):
            if hasattr(zombie, "update"):
                zombie.update()

            if getattr(zombie, 'attack_target_id', None):
                zombie.perform_attack()

            if getattr(zombie, "ready_to_remove", False):
                del self.Zombies[zombie_id]

        # 植物死亡的清理
        for plant in self.Plants:
            if plant.health <= 0:
                plant.kill()

        self.spawn_zombies()

    def render(self):
        self.screen.blit(self.background, (-105, 0))
        self.screen.blit(self.seedband, (150, 0))

        # Sun 计数
        sun_text = self.font.render(f"{self.SunNum}", True, (0, 0, 0))
        sun_text_rect = sun_text.get_rect()
        sun_text_rect.center = (187, 73)
        self.screen.blit(sun_text, sun_text_rect)

        # 卡片
        self.cards.draw(self.screen)

        # 植物
        self.Plants.draw(self.screen)

        # 子弹
        self.BulletGroup.draw(self.screen)

        # 僵尸
        for zombie_id, zombie in self.Zombies.items():
            if hasattr(zombie, 'image') and hasattr(zombie, 'rect'):
                self.screen.blit(zombie.image, zombie.rect)

    def create_zombie(self, zombie_type, position):
        zombie_data = self.zombies_data.get(zombie_type, {})
        if not zombie_data:
            print(f"Zombie type {zombie_type} not found in zombies.json")
            return None
        try:

            from zombies import Zombie
            line_1based = int(round((position[1] - 80) / 99.0)) + 1
            line_1based = max(1, min(5, line_1based))

            zombie_obj = Zombie(
                zombie_type=zombie_type,
                line=line_1based,
                bg=self.screen,
                start_x=position[0],
                engine=self
            )
            return zombie_obj
        except Exception as e:
            print (f"Failed to create zombie  {zombie_type}: {str(e)}")
            return None

    def handle_mouse_move(self,pos):
        """处理鼠标移动事件, 更新拖动位置"""
        if self.DraggingImage:
            self.DraggingPos = pos
        else:
            self.DraggingImage = None

    def handle_mouse_down(self, pos):
        """处理鼠标按下事件"""
        if not self.DraggingCard:
            for card in self.cards:
                if card.rect.collidepoint(pos):
                    card.handle_click()
            else:
                return

        if 145 <= pos[0] <= 875 and 80 <= pos[1] <= 575:
            col = (pos[0] - 145) // 81
            row = (pos[1] - 80) // 99

            if 0 <= row < 5 and 0 <= col < 9:
                plant = self.create_plant(self.DraggingCard.name,
                self.Grids[row][col].rect.left, self.Grids[row][col].rect.top)
                if plant is not None and self.Grids[row][col].planting(plant):
                    self.SunNum -= self.DraggingCard.cost
                    self.DraggingCard.cooldown = self.DraggingCard.max_cooldown
                    self.DraggingCard.CDready = False
                    self.Plants.add(plant)      # type:ignore

        self.DraggingCard = None
        self.DraggingImage = None

    def run(self):
        running = True
        while running:
            current_time = pygame.time.get_ticks()
            self.last_time = current_time

            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.handle_mouse_down(event.pos)
                elif event.type == MOUSEMOTION:
                    if event.buttons[0]:
                        self.handle_mouse_move(event.pos)

            self.update()
            self.render()

            # 渲染拖动的卡片
            if self.DraggingImage:
                mouse_pos = pygame.mouse.get_pos()
                self.screen.blit(self.DraggingImage, (mouse_pos[0] - 35, mouse_pos[1] - 45))

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

    def spawn_zombies(self):
        if not hasattr(self, 'last_spawn_time'):
            self.last_spawn_time = pygame.time.get_ticks()
        current_time = pygame.time.get_ticks()
        if current_time - self.last_spawn_time > 5000:
            self.last_spawn_time = current_time
            if self.current_level and 'AZ' in self.current_level:
                for zombie_data in self.current_level['AZ']:
                    zombie_type, count, row = zombie_data
                    for _ in range(count):
                        # 这里的 y 用于“行推断”，create_zombie 内部会把它对齐到网格行
                        zombie = self.create_zombie(zombie_type, (850, 120 + row * 100))
                        if zombie:
                            zombie_id = f'zombie_{len(self.Zombies)}'
                            self.Zombies[zombie_id] = zombie


class Grid:
    """格子类"""
    def __init__(self, row=0, col=0, length=81, width=99):
        self.rect = pygame.Rect((145 + col * length), (80 + row * width), length, width)
        self.isPlanted = False      # 是否种植了植物
        self.plants = pygame.sprite.OrderedUpdates()
        self.reduplication = True      # 是否可叠种
        self.row = row
        self.col = col


    def update(self):
        """格子更新"""
        if not self.plants:
            self.isPlanted = False

    def planting(self, plant):
        """种植植物"""
        if not self.isPlanted:
            self.plants.add(plant)
            self.isPlanted = True
            return True
        elif self.isPlanted and self.reduplication:
            self.plants.add(plant)
            return True
        return False


class Card(pygame.sprite.Sprite):
    """卡片类(以后兼容僵尸)"""
    def __init__(self, engine, card_type, x, y):
        super().__init__()

        self.engine = engine
        self.data = self.engine.plants_data.get(card_type, {})
        self.name = card_type
        self.cost = self.data.get("cost", 50)
        self.max_cooldown = self.data.get("cooldown", 7.5)

        self.cooldown = 0
        self.CDready = True
        self.sun_ready = True

        self.normal_image = self.load_card_image()
        self.gray_img = self.get_gray_image()
        self.image = self.normal_image
        self.plant_img = all_plants_animations[card_type][0]
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def load_card_image(self):
        try:
            img_path = self.engine.base_dir / self.data.get("card_image")
            image = pygame.image.load(str(img_path)).convert_alpha()
            return image
        except Exception as e:
            print(f"Failed to load card image for {self.name}: {str(e)}")
            placeholder = pygame.Surface((70, 90), pygame.SRCALPHA)
            placeholder.fill((200, 100, 100, 128))
            return placeholder

    def get_gray_image(self):
        gary_img = self.normal_image.copy()
        over_lay = pygame.Surface(self.normal_image.get_size(), pygame.SRCALPHA)
        over_lay.fill((0, 0, 0, 160))
        gary_img.blit(over_lay, (0, 0))
        return gary_img

    def handle_click(self):
        if self.sun_ready and self.CDready and (not self.engine.DraggingCard):
            self.engine.DraggingCard = self
            self.engine.DraggingImage = self.plant_img
        pass

    def update(self):
        current_time = pygame.time.get_ticks()
        delta = (current_time - self.engine.last_update_time) / 1000
        if self.cooldown > 0:
            self.cooldown = max(0, self.cooldown - delta)
        self.image = self.gray_img if (self.engine.DraggingCard == self or
                                       not (self.sun_ready and self.CDready)) else self.normal_image
        self.CDready = True if self.cooldown <= 0 else False
        self.sun_ready = True if self.engine.SunNum >= self.cost else False


if __name__ == "__main__":
    game = GameEngine()
    if game.load_level("1"):
        game.run()
    else:
        print(f"failed to load level 1 ")
