import pygame
from screen import GameTimer, screen1


class Zombie(pygame.sprite.Sprite):
    """
    采用帧动画
    僵尸不同状态的每帧动画做成一个列表
    images为僵尸不同状态动画列表的字典
    约定:
    'walk' -> 正常行走
    'lost_arm_walk' -> 丢失胳膊行走
    'lost_head_walk' -> 丢失脑袋行走
    'attack' -> 正常攻击
    'lost_arm_attack' -> 丢失胳膊攻击
    'lost_head_attack' -> 丢失脑袋攻击
    'dead' -> 正常死亡
    'bang' -> 灰烬死亡
    后续在添加动画
    """

    MAX_HP = 270.0
    BASE_SPEED = 0.6
    WALK_ATTACK_FRAME = 10  # 正常行走转正常攻击关键帧

    def __init__(self, images: dict, line=1, bg=screen1) -> None:
        super().__init__()

        self.status = 'walk'                         # 僵尸的不同阶段,同时用于self.images的索引
        self.line = line                             # 僵尸所在的排数
        self.images = images                         # 帧动画的图片组
        self.img_index = 0                           # 帧动画图片索引
        self.image = images[self.status][self.img_index]  # 这一帧绘制的图片
        self.rect = self.image.get_rect()            # 僵尸的位置矩形
        self.bg = bg

        self.hp = self.MAX_HP                        # 实时血量
        self.speed = self.BASE_SPEED                 # 实时速度
        self.slow = False                            # 是否被减速
        self.has_lost_arm = False                    # 是否丢失手臂
        self.has_lost_head = False                   # 是否丢失头
        self.injury_type = 'normal'                  # 僵尸受到伤害的类型
        self.pending_attack_switch = False           # 等待切换攻击动画
        self.attack_anim_end = False                 # 是否攻击完毕

        self.freezing_timer = GameTimer(0)           # 冻结计时器

    def update(self) -> None:
        self.handle_timers()
        self.attack()
        self.handle_status()
        self.update_animation()
        self.draw()
        self.move()

    def handle_timers(self):
        """处理各种计时器"""
        # 冻结计时器
        if self.freezing_timer.active:
            if self.freezing_timer.is_finished():
                self.speed = self.BASE_SPEED

    def handle_status(self):
        if self.hp <= 0:
            # 死亡时判断最后一次伤害类型
            self.status = 'bang' if self.injury_type == 'bang' else 'dead'

        if self.status in ['attack', 'lost_arm_attack', 'lost_head_attack'] and self.attack_anim_end is True:
            self.status = self._get_walk_status()
            self.img_index = 0

        if self.status in ['walk', 'lost_arm_walk', 'lost_head_walk'] and self.pending_attack_switch is True:
            if self.img_index == self.WALK_ATTACK_FRAME:     # 判断关键帧
                self.status = self._get_attack_status()
                self.img_index = 0

    def update_animation(self):
        """切换当前帧动画"""
        frames = self.images[self.status]
        self.image = frames[self.img_index]

        self.img_index += 1
        if self.img_index >= len(frames):
            self.img_index = 0

    def draw(self):
        """用于绘制图片"""
        self.bg.blit(self.image, self.rect)

    def _get_attack_status(self):
        """根据当前状态和肢体状况返回对应攻击动画key"""
        if self.has_lost_head:
            return 'lost_head_attack'
        elif self.has_lost_arm:
            return 'lost_arm_attack'
        else:
            return 'attack'

    def _get_walk_status(self):
        """根据当前状态和肢体状况返回对应行走动画key"""
        if self.has_lost_head:
            return "lost_head_walk"
        elif self.has_lost_arm:
            return "lost_arm_walk"
        else:
            return "walk"

    def attack(self) -> None:
        ...

    def injured(self, damage_type, damage_value, freeze_duration=0) -> None:
        """
        damage_type: 伤害类型
        damage_value: 伤害大小
        freeze_duration: 冻结时长
        """
        prev_hp = self.hp      # 受伤前血量
        self.hp -= damage_value

        # 肢体丢失判断（只会丢失一次）
        if not self.has_lost_arm and self.hp <= self.MAX_HP * 0.5:
            self.has_lost_arm = True
        if not self.has_lost_head and self.hp <= self.MAX_HP * 0.2:
            self.has_lost_head = True

        if damage_type == 'freezing':
            self.speed = self.BASE_SPEED * (1 / 2)
            self.injury_type = 'normal'
            self.freezing_timer.start(freeze_duration)

        # 死亡处理，只在死亡时记录最后一次伤害类型
        if self.hp <= 0 < prev_hp:
            self.hp = 0
            self.injury_type = damage_type
            self.die()

    def move(self) -> None:
        if self.status not in ['dead', 'bang']:
            self.rect.left = self.rect.left + self.speed

    def die(self):
        self.speed = 0
        self.status = 'dead'
        self.img_index = 0
        self.update_animation()
        pygame.time.delay(100)
        self.kill()


class NormalZombie(Zombie):
    pass
