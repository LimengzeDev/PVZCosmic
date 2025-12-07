import json
import pygame
import sys
from pathlib import Path
from pygame.locals import *

# 方便 zombies.py 调用 GameEngine 实例
game_instance = None
base_dir = Path(__file__).parent

# 在文件开头添加Bullet类定义
class Bullet(pygame.sprite.Sprite):
    def __init__(self, plant_type, position, damage, speed=5, effect=None):
        super().__init__()
        self.plant_type = plant_type
        self.damage = damage
        self.speed = speed
        self.effect = effect  # 特殊效果，如冰冻、火焰等
        
        # 加载子弹图片
        try:
            if plant_type == "Peashooter":
                img_path = base_dir / "images/plants/PB00.gif"
                self.image = pygame.image.load(str(img_path)).convert_alpha()
            elif plant_type == "SnowPea":
                img_path = base_dir / "images/plants/SnowPea.gif"
                self.image = pygame.image.load(str(img_path)).convert_alpha()
            else:
                # 默认子弹
                self.image = pygame.Surface((15, 15), pygame.SRCALPHA)
                pygame.draw.circle(self.image, (0, 255, 0), (7, 7), 7)
        except :
            self.image = pygame.Surface((15, 15), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (0, 255, 0), (7, 7), 7)
            
        self.rect = self.image.get_rect()
        self.rect.centerx = position[0] + 40  # 从植物右侧发射
        self.rect.centery = position[1] + 40
        
        # 记录子弹所在行
        self.row = int((position[1] - 80) // 99)
        
    def update(self):
        """更新子弹位置"""
        self.rect.x += self.speed
        
        # 如果子弹超出屏幕右侧，则删除
        if self.rect.left > 900:
            self.kill()
            
    def check_collision(self, zombies):
        """检查子弹与僵尸的碰撞"""
        for zombie_id, zombie in list(zombies.items()):
            if hasattr(zombie, 'rect') and self.rect.colliderect(zombie.rect):
                # 检查是否在同一行
                if zombie.row_index == self.row:
                    # 对僵尸造成伤害
                    zombie.hp -= self.damage
                    
                    # 应用特殊效果
                    if self.effect == "freeze":
                        # 冰冻效果：减速
                        zombie.speed = max(0.2, zombie.speed * 0.5)
                        # 可以在这里添加冰冻视觉效果
                    
                    self.kill()
                    return True
        return False


class GameEngine:
    def __init__(self, levels_folder="levels", data_folder="data"):
        global game_instance
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
        self.W = 880
        self.H = 600
        self.C = 9
        self.LawnMowerX = 70
        self.SunNum = 50
        self.Chose = 0
        self.ChoseCard = ""
        self.MPID = ""
        self.ArCard = []
        self.ArPCard = {}
        self.ArSun = []
        self.AllPlants = {}
        self.Zombies = {}
        self.DraggingCard = None
        self.DraggingPos = (0, 0)
        self.Grid = [[None for _ in range(9)] for _ in range(5)]

        self.font = pygame.font.SysFont('Arial', 16)
        self.big_font = pygame.font.SysFont('Arial', 24)
        self.last_time = pygame.time.get_ticks()
        self.card_gray_images = {}
        self.BulletGroup = pygame.sprite.Group()
        self.last_bullet_time = pygame.time.get_ticks()
        self.last_update_time = pygame.time.get_ticks()
        
        # ... 其余初始化代码 ...
        # 设置全局实例
        game_instance = self

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
        self.load_card_images()

        bg_path = self.current_level.get("backgroundImage", "images/interface/background1.jpg")
        try:
            self.background = pygame.image.load(str(self.base_dir / bg_path))
        except Exception as e:
            print(f"Failed to load background {bg_path}: {str(e)}")
            self.background = pygame.Surface((880, 600))
            self.background.fill((100, 200, 100))

    def init_plant_cards(self):
        self.ArCard = []
        self.ArPCard = {}

        for i, plant_type in enumerate(self.PName):
            plant_data = self.plants_data.get(plant_type, {})
            card_data = {
                "DID": f"Card{plant_type}",
                "PName": plant_type,
                "Index": i,
                "Rect": pygame.Rect(10, 80 + i * 70, 70, 90),  # vertical arrangement
                "Cost": plant_data.get("cost", 100),
                "MaxCooldown": plant_data.get("cooldown", 7.5),
                "Cooldown": 0,
                "CDReady": 1,
                "SunReady": 1,
                "Cooling": False,
                "ImgPath": plant_data.get("card_image", "")
            }
            self.ArCard.append(card_data)
            self.ArPCard[plant_type] = card_data

    def load_card_images(self):
        self.card_images = {}
        self.card_gray_images = {}

        for plant_type, plant_data in self.plants_data.items():
            if plant_type in self.PName:
                try:
                    img_path = self.base_dir / plant_data["card_image"]
                    normal_img = pygame.image.load(str(img_path)).convert_alpha()
                    self.card_images[plant_type] = normal_img
                    gray_img = self.convert_to_grayscale(normal_img.copy())
                    self.card_gray_images[plant_type] = gray_img
                except Exception as e:
                    print(f"Failed to load card image for {plant_type}: {str(e)}")
                    placeholder = pygame.Surface((70, 90), pygame.SRCALPHA)
                    placeholder.fill((200, 100, 100, 128))
                    self.card_images[plant_type] = placeholder
                    self.card_gray_images[plant_type] = self.convert_to_grayscale(placeholder.copy())

    def convert_to_grayscale(self, surface):
        gray_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        for x in range(surface.get_width()):
            for y in range(surface.get_height()):
                r, g, b, a = surface.get_at((x, y))
                gray = int(0.21 * r + 0.72 * g + 0.07 * b)
                gray_surface.set_at((x, y), (gray, gray, gray, a))
        return gray_surface




    def create_plant(self, plant_type, row, col):
        """创建植物，添加攻击相关属性"""
        try:
            from plants import Plant
            plant = Plant(
                self,
                plant_type,
                row,
                col,
            )

            return plant
        except Exception as e:
            print(f"Failed to create plant {plant_type}: {str(e)}")
            return None

    def update_plant_attacks(self, current_time):
        """更新植物攻击逻辑"""
        for plant_id, plant in self.AllPlants.items():
            attack_data = plant.attack_data
            if not attack_data:
                continue
                
            attack_interval = attack_data.get("interval", 2000)  # 默认2秒攻击一次
            
            # 检查是否到了攻击时间
            if current_time - plant.last_attack_time >= attack_interval:
                # 检查该行是否有僵尸
                if self.has_zombies_in_row(plant.row):
                    self.create_bullet(plant)
                    plant.last_attack_time = current_time

    def has_zombies_in_row(self, row):
        """检查指定行是否有僵尸"""
        for zombie_id, zombie in self.Zombies.items():
            if hasattr(zombie, 'row_index') and zombie.row_index == row:
                return True
        return False

    def create_bullet(self, plant):
        """根据植物类型创建子弹"""
        attack_data = plant.attack_data
        bullet_type = attack_data.get("type", "pea")
        damage = attack_data.get("damage", 20)
        
        if bullet_type == "pea":
            effect = None
            if plant.type == "SnowPea":
                effect = "freeze"
                
            bullet = Bullet(
                plant.type,
                plant.position,
                damage,
                effect=effect
            )
            self.BulletGroup.add(bullet)
            
        elif bullet_type == "instant":
            # 瞬时攻击（如土豆地雷）
            self.instant_attack(plant, damage)
            
        # 可以在这里添加其他类型的攻击

    def instant_attack(self, plant, damage):
        """瞬时攻击（对范围内的所有僵尸造成伤害）"""
        row = plant.row
        for zombie_id, zombie in list(self.Zombies.items()):
            if hasattr(zombie, 'row_index') and zombie.row_index == row:
                # 检查僵尸是否在攻击范围内
                if self.is_zombie_in_range(zombie, plant):
                    zombie.hp -= damage
                    # 可以在这里添加攻击特效

    def is_zombie_in_range(self, zombie, plant):
        """检查僵尸是否在植物的攻击范围内"""
        plant_right = plant.position[0] + 80
        zombie_left = zombie.rect.left
        
        # 僵尸在植物右侧且在攻击范围内
        return zombie_left <= plant_right + 200  # 假设攻击范围为200像素

    def update_bullets(self):
        """更新所有子弹状态"""
        self.BulletGroup.update()
        
        # 检查子弹与僵尸的碰撞
        for bullet in self.BulletGroup.sprites():
            bullet.check_collision(self.Zombies)

    def update(self):
        current_time = pygame.time.get_ticks()
        delta = (current_time - self.last_update_time) / 1000.0
        self.last_update_time = current_time

        # 卡片冷却
        for card in self.ArCard:
            if card["Cooldown"] > 0:
                card["Cooldown"] = max(0, card["Cooldown"] - delta)
                card["CDReady"] = 1 if card["Cooldown"] <= 0 else 0
            card["SunReady"] = 1 if self.SunNum >= card["Cost"] else 0

        # 植物动画
        for plant_id, plant in self.AllPlants.items():
            plant.update()

        # 植物攻击
        self.update_plant_attacks(current_time)
        
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
        for plant_id, plant in list(self.AllPlants.items()):
            if plant.health <= 0:
                for row in range(5):
                    for col in range(9):
                        if self.Grid[row][col] == plant_id:
                            self.Grid[row][col] = None
                del self.AllPlants[plant_id]

        self.spawn_zombies()

    def render(self):
        self.screen.blit(self.background, (-105, 0))

        # Sun 计数
        sun_text = self.big_font.render(f"Sun: {self.SunNum}", True, (255, 255, 0))
        self.screen.blit(sun_text, (10, 10))

        # 卡片
        for card in self.ArCard:
            plant_type = card["PName"]
            if plant_type in self.card_images:
                if card["CDReady"] and card["SunReady"]:
                    img = self.card_images[plant_type]
                else:
                    img = self.card_gray_images[plant_type]

                if card != self.DraggingCard:
                    self.screen.blit(img, card["Rect"])
                    cost_text = self.font.render(str(card["Cost"]), True,
                                                 (255, 255, 0) if card["SunReady"] else (150, 150, 150))
                    self.screen.blit(cost_text, (card["Rect"].x + 5, card["Rect"].y + 70))

        # 植物
        for plant_id, plant in self.AllPlants.items():
            frame = plant.get_current_frame()
            self.screen.blit(frame, plant.position)

        # 子弹
        self.BulletGroup.draw(self.screen)

        # 僵尸
        for zombie_id, zombie in self.Zombies.items():
            if hasattr(zombie, 'image') and hasattr(zombie, 'rect'):
                self.screen.blit(zombie.image, zombie.rect)

    def handle_mouse_up(self, pos):

        """处理鼠标释放事件，开始拖动卡片"""
        for card in self.ArCard:
            if card['Rect'].collidepoint(pos) and card["CDReady"] and card["SunReady"]:
                self.DraggingCard = card
                self.DraggingPos = pos
                return True
        return False

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
                engine=self   #blablabla
            )
            '''
            zombie_obj.hp = zombie_data.get('health', zombie_obj.MAX_HP)
            zombie_obj.speed = zombie_data.get('speed', zombie_obj.BASE_SPEED)
            '''
            return zombie_obj
        except Exception as e:
            print (f"Failed to create zombie  {zombie_type}: {str(e)}")
            return None

    def handle_mouse_move(self,pos):
        """处理鼠标移动事件, 更新拖动位置"""
        if self.DraggingCard:
            self.DraggingPos = pos
            return True
        return False

    def handle_mouse_down(self, pos):
        """处理鼠标按下事件，放置植物"""
        if not self.DraggingCard:
            return False

        if 145 <= pos[0] <= 875 and 80 <= pos[1] <= 575:
            col = (pos[0] - 145) // 81
            row = (pos[1] - 80) // 99

            if 0 <= row < 5 and 0 <= col < 9:
                if self.Grid[row][col] is None:
                    self.SunNum -= self.DraggingCard["Cost"]
                    self.DraggingCard["Cooldown"] = self.DraggingCard["MaxCooldown"]
                    self.DraggingCard["CDReady"] = 0

                    plant = self.create_plant(self.DraggingCard["PName"], row, col)
                    if plant:
                        plant_id = f"plant_{len(self.AllPlants)}"
                        self.AllPlants[plant_id] = plant
                        self.Grid[row][col] = plant_id

        self.DraggingCard = None
        return True

# ... 其余代码保持不变 ...

    def run(self):
        running = True
        while running:
            current_time = pygame.time.get_ticks()
            dt = (current_time - self.last_time) / 1000.0
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
                elif event.type == MOUSEBUTTONUP:
                    if event.button == 1:
                        self.handle_mouse_up(event.pos)

            self.update()
            self.render()

            # 渲染拖动的卡片
            if self.DraggingCard:
                mouse_pos = pygame.mouse.get_pos()
                img = self.card_images[self.DraggingCard["PName"]]
                self.screen.blit(img, (mouse_pos[0] - 35, mouse_pos[1] - 45))

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
                        # 仍按原有协议：这里的 y 用于“行推断”，create_zombie 内部会把它对齐到网格行
                        zombie = self.create_zombie(zombie_type, (850, 120 + row * 100))
                        if zombie:
                            zombie_id = f'zombie_{len(self.Zombies)}'
                            self.Zombies[zombie_id] = zombie


class Lattice:
    """格子类"""
    def __init__(self, row=0, col=0):
        self.rect = pygame.Rect((145 + col * 81), (80 + row * 99), 81, 99)
        self.isPlanted = False
        self.plants = pygame.sprite.OrderedUpdates()
        self.reduplication = False
        self.row = row
        self.col = col


    def update_plants(self):
        self.plants.update()

if __name__ == "__main__":
    game = GameEngine()
    if game.load_level("1"):
        game.run()
    else:
        print(f"failed to load level 1 ")
