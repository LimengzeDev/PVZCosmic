import pygame
import json
from pathlib import Path
from PIL import Image, ImageSequence

base_dir = Path(__file__).parent
file_path = base_dir / "data" / "plants.json"
try:
    with open(file_path, "r") as f:
        plants_data = json.load(f)
except Exception as e:
    plants_data = {}
    print(f"filed to load {file_path}: {str(e)}")

def preload_plant_resources():
    plants_cache = {}
    for plants_type, data in plants_data.items():
        try:
            bath_path = base_dir / data['animation']
            animations = load_gif(bath_path)
            plants_cache[plants_type] = animations
        except Exception as _e:
            print(f"failed to preload plant: {plants_type}: {str(_e)}")
    return plants_cache

def load_gif(gif_path):
    animations = []
    try:
        with Image.open(gif_path) as img:
            for frame in ImageSequence.Iterator(img):
                frame = frame.convert("RGBA")
                pygame_frame = pygame.image.fromstring(
                    frame.tobytes(), frame.size, frame.mode
                )
                animations.append(pygame_frame)
    except Exception as _e:
        print(f"failed to load GIF {gif_path}: {str(_e)}")
    return animations

all_plants_animations = preload_plant_resources()


class Bullet(pygame.sprite.Sprite):

    """
    子弹基类
    类型1: 'normal' -> 正常
    类型2: 'gone' -> 碰撞后的消失动画
    """

    def __init__(self, pos=(0, 0)):
        super().__init__()
        self.img_index = 0
        self.images = dict(normal=[pygame.image.load(
            "D:\\FeverGames Apps\\pythonProject1\\PVZCosmic\\images\\Plants\\PB01.gif")], gone=pygame.image.load(
            "D:\\FeverGames Apps\\pythonProject1\\PVZCosmic\\images\\Plants\\PeaBulletHit.gif"))
        self.status = 'normal'
        self.image = self.images[self.status][self.img_index]
        self.rect = self.images['normal'][0].get_rect()
        self.rect.x, self.rect.y = pos[0], pos[1]

        self.dmg_value = 50
        self.dmg_type = 'normal'
        self.speed = -1.2

    def update_animation(self):
        """更新动画帧"""
        frames = self.images[self.status]
        self.image = frames[self.img_index]
        self.img_index += 1
        if self.img_index >= len(frames):
            self.img_index = 0

    def attack(self, zombie):
        """子弹攻击僵尸,碰撞后调用,之后加碰撞判断"""
        zombie.injured(self.dmg_type, self.dmg_value)
        self.status = 'gone'
        self.speed = 0

    def move(self):
        self.rect.x += self.speed

    def draw(self) -> None: ...
    def update(self) -> None: ...


class Plant(pygame.sprite.Sprite):
    """通用植物"""

    def __init__(self, engine, plant_type, row, col):
        super().__init__()
        self.engine = engine
        self.animation = all_plants_animations[plant_type]
        self.frame_index = 0
        self.image = self.animation[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = 145 + col * 81
        self.rect.y = 80 + row * 99
        self.position = self.rect.x, self.rect.y

        self.anim_interval = 1e-25
        now =pygame.time.get_ticks()

        self.animation_timer = now
        self.last_attack_time = now

        self.row = row
        self.col = col
        self.type = plant_type
        self.health = plants_data.get(plant_type, {}).get("health", 100)
        self.attack_data = plants_data.get(plant_type, {}).get("attack", {})
        self.interval = self.attack_data.get("interval", 2000)

    def _update_image(self,now):
        if now - self.animation_timer >= self.anim_interval:
            self.frame_index = (self.frame_index + 1) % len(self.animation)
            self.image = self.animation[self.frame_index]

    def get_current_frame(self):
        return self.image

    def attack(self, now):
        if self.attack_data:
            if now - self.last_attack_time >= self.interval:
                self.engine.BulletGroup.add(self.create_bullet())


    def create_bullet(self):
        pass

    def update(self):
        now = pygame.time.get_ticks()
        self._update_image(now)
       # self.attack(now)
