import pygame
import json
from pathlib import Path
from PIL import Image, ImageSequence

#下载植物资源
base_dir = Path(__file__).parent
file_path = base_dir / "data" / "plants.json"
try:
    with open(file_path, "r") as f:
        plants_data = json.load(f)
except Exception as e:
    plants_data = {}
    print(f"filed to load {file_path}: {str(e)}")

def preload_plant_resources():
    """预加载资源"""
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
    """下载gif动图"""
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
    """子弹基类"""

    def __init__(self, engine, bullet_type, position, damage, speed=5, effect=None):
        """
        :param engine: GameEngine 实例
        :param bullet_type: 子弹类型
        :param position: 子弹所在位置
        :param damage: 子弹伤害
        :param speed: 子弹移动速度
        :param effect: 子弹效果
        """
        super().__init__()

        self.engine = engine
        self.bullet_type = bullet_type
        self.damage = damage
        self.speed = speed
        self.effect = effect

        #获取子弹图片
        try:
            if self.bullet_type == 'pea':
                img_path = base_dir / "images/plants/PB00.gif"
                self.image =pygame.image.load(str(img_path))
            else:
                self.image = pygame.Surface((15, 15), pygame.SRCALPHA)

        except pygame.error:
            self.image = pygame.Surface((15, 15), pygame.SRCALPHA)

        #动画初始化
        self.rect = self.image.get_rect()
        self.rect.centerx = position[0] + 40    #子弹从右边发射
        self.rect.centery = position[1] + 40
        self.row = int((position[1] - 80) // 99)    #子弹所在行

    def check_collision(self,zombies):
        """检查是否与僵尸碰撞"""
        for zombie_id, zombie in list(zombies.items()):
            #检查是否在同一行
            if hasattr(zombie, 'rect') and self.rect.colliderect(zombie.rect):
                #对僵尸造成伤害
                zombie.hp -= self.damage
                self.kill()

    def attack(self, zombie):
        """后续完善攻击逻辑"""
        pass

    def move(self):
        self.rect.x += self.speed

        if self.rect.left > 900:
            self.kill()     #超出屏幕外清除

    def update(self) -> None:
        self.move()
        self.check_collision(self.engine.Zombies)


class Plant(pygame.sprite.Sprite):
    """通用植物"""

    def __init__(self, engine, plant_type, row, col):
        """
        :param engine: GameEngine 实例
        :param plant_type: 植物种类
        :param row: 所在行
        ;param col: 所在列
        """
        super().__init__()
        self.engine = engine

        #动画初始化
        self.animation = all_plants_animations[plant_type]      #植物动画数据
        self.frame_index = 0        #帧动画图片索引
        self.image = self.animation[self.frame_index]       #当前帧
        self.rect = self.image.get_rect()
        self.rect.x = 145 + col * 81
        self.rect.y = 80 + row * 99
        self.position = self.rect.x, self.rect.y

        self.anim_interval = 1e-25      #动画两帧间隔
        now =pygame.time.get_ticks()

        self.animation_timer = now      #动画计时器
        self.last_attack_time = now     #攻击计时器

        #植物初始化
        self.row = row
        self.col = col
        self.type = plant_type
        self.health = plants_data.get(plant_type, {}).get("health", 100)
        self.attack_data = plants_data.get(plant_type, {}).get("attack", {})        #攻击数据
        self.interval = self.attack_data.get("interval", 2000)      #攻击冷却时间

    def _update_image(self,now):
        """帧动画图片更新"""
        if now - self.animation_timer >= self.anim_interval:
            self.frame_index = (self.frame_index + 1) % len(self.animation)
            self.image = self.animation[self.frame_index]

    def get_current_frame(self):
        """获取当前帧"""
        return self.image

    def attack(self, now):
        """攻击"""
        if self.attack_data:    #有攻击数据才攻击
            bullet = self.create_bullet()
            if now - self.last_attack_time >= self.interval and bullet:
                self.engine.BulletGroup.add(bullet)
                self.last_attack_time = now


    def create_bullet(self):
        """创建子弹实例"""
        if not self.attack_data:
            return None
        else:
            bullet_type = self.attack_data.get('type', None)
            attack_effect = self.attack_data.get('effect', None)
            damage = self.attack_data.get('damage', 200)
            speed = 5
            bullet = Bullet(self.engine, bullet_type, self.position, damage, speed, attack_effect)
            return bullet



    def update(self):
        """植物更新"""
        now = pygame.time.get_ticks()
        self._update_image(now)
        self.attack(now)
