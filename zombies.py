import pygame
from screen import GameTimer, screen1
import weakref

class Zombie(pygame.sprite.Sprite):
    MAX_HP = 270.0
    BASE_SPEED = 0.6  # negative for moving left
    WALK_ATTACK_FRAME = 10

    def __init__(self, images: dict, line=1, bg=screen1, start_x=850) -> None:
        super().__init__()
        self.status = 'walk'
        self.line = line
        self.images = images
        self.img_index = 0
        self.image = images[self.status][self.img_index]
        self.rect = self.image.get_rect()
        self.bg = bg
        self.rect.left = start_x
        self.rect.top = 120 + (line - 1) * 100

        self.hp = self.MAX_HP
        self.speed = self.BASE_SPEED
        self.slow = False
        self.has_lost_arm = False
        self.has_lost_head = False
        self.injury_type = 'normal'
        self.pending_attack_switch = False
        self.attack_anim_end = False

        self.freezing_timer = GameTimer(0)

    def get_game_instance(self):
        """安全获取游戏实例的方法"""
        try:
            from levelManager import game_instance_ref
            if game_instance_ref is not None:
                instance = game_instance_ref()
                if instance is not None:
                    return instance
        except ImportError:
            pass
        return None

    def update(self) -> None:
        self.handle_timers()
        self.attack()
        self.handle_status()
        self.update_animation()
        self.draw()
        self.move()

    def handle_timers(self):
        """处理所有计时器逻辑"""
        if hasattr(self, 'freezing_timer') and self.freezing_timer.active:
            if self.freezing_timer.is_finished():
                self.speed = self.BASE_SPEED

    def handle_status(self):
        """处理僵尸状态变化"""
        if self.hp <= 0:
            self.status = 'bang' if self.injury_type == 'bang' else 'dead'

        if self.status in ['attack', 'lost_arm_attack', 'lost_head_attack'] and self.attack_anim_end is True:
            self.status = self._get_walk_status()
            self.img_index = 0

        if self.status in ['walk', 'lost_arm_walk', 'lost_head_walk'] and self.pending_attack_switch is True:
            if self.img_index == self.WALK_ATTACK_FRAME:
                self.status = self._get_attack_status()
                self.img_index = 0

    def update_animation(self):
        """更新动画帧"""
        frames = self.images[self.status]
    
        # 控制动画速度的因子 (值越大播放越快)
        speed_factor = 0.5  # 默认1.0，小于1变慢，大于1变快
    
        self.img_index += speed_factor  # 修改这里控制速度
    
        if self.img_index >= len(frames):
            self.img_index = 0
            if self.status in ['attack', 'lost_arm_attack', 'lost_head_attack']:
                self.attack_anim_end = True
    
        self.image = frames[int(self.img_index)]  # 转换为整数索引

    def draw(self):
        """绘制僵尸"""
        self.bg.blit(self.image, self.rect)

    def _get_attack_status(self):
        """获取攻击状态"""
        if self.has_lost_head:
            return 'lost_head_attack'
        elif self.has_lost_arm:
            return 'lost_arm_attack'
        else:
            return 'attack'

    def _get_walk_status(self):
        """获取行走状态"""
        if self.has_lost_head:
            return "lost_head_walk"
        elif self.has_lost_arm:
            return "lost_arm_walk"
        else:
            return "walk"

    def attack(self):
        """检查前方植物并进行攻击"""
        game_instance = self.get_game_instance()
        if game_instance is None:
            return

        if not hasattr(game_instance, 'Plants'):
            return

        collided = False
        for plant_id, plant in list(game_instance.Plants.items()):
            if not plant or 'position' not in plant or 'anim' not in plant:
                continue
                
            try:
                plant_rect = pygame.Rect(plant['position'][0], plant['position'][1],
                                       plant['anim'].frames[0].get_width(),
                                       plant['anim'].frames[0].get_height())
                if self.rect.colliderect(plant_rect):
                    collided = True
                    self.pending_attack_switch = True
                    plant['health'] -= 1
                    if plant['health'] <= 0:
                        del game_instance.Plants[plant_id]
                    break
            except (AttributeError, KeyError, IndexError) as e:
                print(f"Error processing plant {plant_id}: {str(e)}")
                continue
                
        if not collided:
            self.pending_attack_switch = False

    def injured(self, damage_type, damage_value, freeze_duration=0) -> None:
        """处理受伤逻辑"""
        prev_hp = self.hp
        self.hp -= damage_value

        if not self.has_lost_arm and self.hp <= self.MAX_HP * 0.5:
            self.has_lost_arm = True
        if not self.has_lost_head and self.hp <= self.MAX_HP * 0.2:
            self.has_lost_head = True

        if damage_type == 'freezing':
            self.speed = self.BASE_SPEED / 2
            self.injury_type = 'normal'
            self.freezing_timer.start(freeze_duration)

        if self.hp <= 0 < prev_hp:
            self.hp = 0
            self.injury_type = damage_type
            self.die()

    def move(self) -> None:
        """移动僵尸"""
        if self.status not in ['dead', 'bang']:
            self.rect.left += self.speed

    def die(self):
        """处理死亡逻辑"""
        self.speed = 0
        self.status = 'dead'
        self.img_index = 0
        self.update_animation()
        pygame.time.delay(100)
        self.kill()


class NormalZombie(Zombie):
    pass