import pygame
import json
from pathlib import Path

bath_dir = Path(__file__).parent
file_path = bath_dir / "data"  / "plants.json"
try:
    with open(file_path, "r") as f:
        plants_data = json.load(f)
except Exception as e:
    plants_data = {}
    print(f"filed to load {file_path}: {str(e)}")


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


class PeaBullet(Bullet):
    ...


class Plant(pygame.sprite.Sprite):
    """
    植物状态
    healthy
    等
    """

    MAX_HP = 300
    ATTACK_FRAME = 10

    def __init__(self, images: dict, pos):
        super().__init__()
        self.status = 'healthy'
        self.img_index = 0
        self.images = images
        self.rect = images['healthy'][0].get_rect()
        self.rect.x, self.rect.y = pos[0], pos[1]
        self.image = self.images[self.status][self.img_index]

        self.bullet = PeaBullet
        self.hp = self.MAX_HP

    def attack(self, game_engine):
        if self.img_index == self.ATTACK_FRAME:
            game_engine.BulletGroup.add(self.bullet((53, 10)))

    def injured(self) -> None: ...
    def update_animation(self) -> None: ...
    def draw(self) -> None: ...

    def update(self, game_engine) -> None:
        self.attack(game_engine)
