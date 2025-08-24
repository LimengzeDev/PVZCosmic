import json
import os
import pygame
import sys
from pathlib import Path
from pygame.locals import *
from PIL import Image, ImageSequence  # For GIF animation support

# 方便 zombies.py 调用 GameEngine 实例
game_instance = None

class AnimatedSprite:
    def __init__(self, gif_path, position=(0, 0)):
        self.frames = []
        self.current_frame = 0
        self.animation_speed = 0.1
        self.time_since_last_frame = 0
        self.position = position
        self.load_gif(gif_path)
        self.last_update_time = pygame.time.get_ticks()

    def load_gif(self, gif_path):
        """Load GIF animation using PIL and convert to pygame surfaces"""
        try:
            with Image.open(gif_path) as img:
                for frame in ImageSequence.Iterator(img):
                    frame = frame.convert("RGBA")
                    pygame_frame = pygame.image.fromstring(
                        frame.tobytes(), frame.size, frame.mode
                    )
                    self.frames.append(pygame_frame)
        except Exception as e:
            print(f"Failed to load GIF {gif_path}: {str(e)}")
            placeholder = pygame.Surface((50, 50), pygame.SRCALPHA)
            placeholder.fill((255, 0, 255, 128))
            self.frames = [placeholder]

    def update(self, dt):
        """Update animation frames"""
        self.time_since_last_frame += dt
        if self.time_since_last_frame >= self.animation_speed:
            self.time_since_last_frame = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)

    def get_current_frame(self):
        return self.frames[self.current_frame]

<<<<<<< HEAD
=======
def get_up_pos(event):
    """
    获取鼠标松开位置
    若在个子范围内返回格子坐标
    不在则返回 None
    """
    if event.type == pygame.MOUSEBUTTONUP:
        if 145 <= event.pos[0] <= 875 and 80 <= event.pos[1] <= 575:
            return event.pos[0] // 85 + 1, event.pos[1] // 95 + 1
        else:
            return None
>>>>>>> bf75a75bcbe84d392f676603496e4522da1b594e

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
        self.last_update_time = pygame.time.get_ticks()

        # 设置全局实例
        game_instance = self
        self.preload_zombie_resources()

    def preload_zombie_resources(self):
        """预加载所有僵尸动画资源"""
        self.zombie_cache = {}
        for zombie_type, data in self.zombies_data.items():
            try:
                animations = {}
                for state, state_data in data["animations"].items():
                    frames = []
                    base_path = self.base_dir / state_data['path']
                    for i in range(1, state_data['frames'] + 1):
                        img_path = base_path / f"{i}.png"
                        img = pygame.image.load(str(img_path)).convert_alpha()
                        frames.append(img)
                    animations[state] = frames
                self.zombie_cache[zombie_type] = animations
            except Exception as e:
                print(f"Failed to preload zombie {zombie_type}: {str(e)}")

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

    def create_plant(self, plant_type, position):
        plant_data = self.plants_data.get(plant_type, {})
        if not plant_data:
            print(f"Plant type {plant_type} not found in plants.json")
            return None
        try:
            anim_path = self.base_dir / plant_data["animation"]
            anim = AnimatedSprite(str(anim_path))
            return {
                "type": plant_type,
                "position": position,
                "anim": anim,
                "health": plant_data.get("health", 100),
                "cooldown": 0
            }
        except Exception as e:
            print(f"Failed to create plant {plant_type}: {str(e)}")
            return None

# ...前略（保持和你之前的一样）...

    def create_zombie(self, zombie_type, position):
        zombie_data = self.zombies_data.get(zombie_type, {})
        if not zombie_data:
            print(f"Zombie type {zombie_type} not found in zombies.json")
            return None
        try:
            animations = {}
            for state, state_data in zombie_data["animations"].items():
                frames = []
                base_path = self.base_dir / state_data['path']
                for i in range(1, state_data['frames'] + 1):
                    img_path = base_path / f"{i}.png"
                    frames.append(pygame.image.load(str(img_path)).convert_alpha())
                animations[state] = frames

            from zombies import Zombie
            line_1based = int(round((position[1] - 80) / 99.0)) + 1
            line_1based = max(1, min(5, line_1based))

            zombie_obj = Zombie(
                animations,
                line=line_1based,
                bg=self.screen,
                start_x=position[0],
                engine=self   # 传入 GameEngine 实例
            )
            zombie_obj.hp = zombie_data.get('health', zombie_obj.MAX_HP)
            zombie_obj.speed = zombie_data.get('speed', zombie_obj.BASE_SPEED)
            return zombie_obj
        except Exception as e:
            print(f"Failed to create zombie {zombie_type}: {str(e)}")
            return None

# ...后续 update/render 等和之前版本保持一致...


    def handle_mouse_down(self, pos):
        """处理鼠标按下事件，开始拖动卡片"""
        for card in self.ArCard:
            if card["Rect"].collidepoint(pos) and card["CDReady"] and card["SunReady"]:
                self.DraggingCard = card
                self.DraggingPos = pos
                return True
        return False

    def handle_mouse_move(self, pos):
        """处理鼠标移动事件，更新拖动位置"""
        if self.DraggingCard:
            dx = pos[0] - self.DraggingPos[0]
            dy = pos[1] - self.DraggingPos[1]
            self.DraggingPos = pos
            return True
        return False

    def handle_mouse_up(self, pos):
        """处理鼠标释放事件，放置植物"""
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

                    plant_x = 145 + col * 81 + 0
                    plant_y = 80 + row * 99 - 0
                    plant = self.create_plant(self.DraggingCard["PName"], (plant_x, plant_y))
                    if plant:
                        plant_id = f"plant_{len(self.AllPlants)}"
                        self.AllPlants[plant_id] = plant
                        self.Grid[row][col] = plant_id

        self.DraggingCard = None
        return True

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

            self.update(dt)
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
    
    def update(self, dt):
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
            plant["anim"].update(dt)

        # 僵尸更新 & 攻击 & 清理
        for zombie_id, zombie in list(self.Zombies.items()):
            if hasattr(zombie, "update"):
                zombie.update()

            # 若处于攻击状态/已有目标，按冷却触发伤害（Zombie 内部也会做一次）
            if getattr(zombie, 'attack_target_id', None):
                zombie.perform_attack()

            # 死亡动画结束/越界 → 移除
            if getattr(zombie, "ready_to_remove", False):
                del self.Zombies[zombie_id]

        # 植物死亡的清理：从网格撤除
        for plant_id, plant in list(self.AllPlants.items()):
            if plant.get('health', 0) <= 0:
                for row in range(5):
                    for col in range(9):
                        if self.Grid[row][col] == plant_id:
                            self.Grid[row][col] = None
                del self.AllPlants[plant_id]

        self.spawn_zombies()    
    
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
            frame = plant["anim"].get_current_frame()
            self.screen.blit(frame, plant["position"])

        # 僵尸
        for zombie_id, zombie in self.Zombies.items():
            if hasattr(zombie, 'image') and hasattr(zombie, 'rect'):
                self.screen.blit(zombie.image, zombie.rect)

    @staticmethod
    def get_up_pos(event):
        """
            获取鼠标松开位置
            若在个子范围内返回格子坐标
            不在则返回 None
        """
        if event.type == pygame.MOUSEBUTTONUP:
            if 145 <= event.pos[0] <= 875 and 80 <= event.pos[1] <= 575:
                return (event.pos[0] - 145) // 85 + 1, (event.pos[1] - 80) // 95 + 1
            else:
                return None

class Lattice:
    """格子类"""
    def __init__(self, row=0, col=0):
        self.rect = pygame.Rect((145 + col * 81), (80 + row * 99), 81, 99)
        self.isPlanted = False
        self.plants: pygame.sprite.Group = pygame.sprite.OrderedUpdates()
        self.reduplication = False
        self.row = row
        self.col = col

    def planted(self, event, plant):
        if event == pygame.MOUSEBUTTONUP:
            if self.rect.collidepoint(event.pos) and event.button == 1:
                if self.reduplication is True:
                    self.plants.add(plant)
                    self.isPlanted = True
                elif self.isPlanted is False and len(self.plants) == 0:
                    self.plants.add(plant)
                    self.isPlanted = True

    def update_plants(self):
        if len(self.plants) == 0:
            self.isPlanted = False
        else:
            self.isPlanted = True
        self.plants.update()

if __name__ == "__main__":
    game = GameEngine()
    if game.load_level("1"):
        game.run()
    else:
        print(f"Failed to load level 1.")
