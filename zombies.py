import pygame

# —— 与 GameEngine 保持一致的草坪网格参数 ——
TILE_LEFT = 145
TILE_TOP = 80
TILE_W = 81
TILE_H = 99


class Zombie(pygame.sprite.Sprite):
    """通用僵尸：行走→接触植物→攻击→（植物死）继续走 / （僵尸死）播放死亡动画"""

    BASE_SPEED = 0.8
    MAX_HP = 100
    ATTACK_DAMAGE = 8
    ATTACK_INTERVAL = 600
    ANIM_INTERVAL = 1e-25
    CONTACT_PAD = 90
    DEAD_REMOVE_DELAY = 800

    def __init__(self, animations, line=1, bg=None, start_x=850, engine=None):
        """
        :param animations: dict {"walk":[Surface...], "attack":[...], "dead":[...]}
        :param line: 1-based 行号
        :param bg:   屏幕 Surface
        :param start_x: 初始 x
        :param engine: GameEngine 实例
        """
        super().__init__()
        self.animations = animations
        self.engine = engine

        if "walk" not in self.animations:
            any_state = next(iter(self.animations.keys()))
            self.state = any_state
        else:
            self.state = "walk"

        self.frames = self.animations[self.state]
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()

        self.row_index = max(0, min(4, (line - 1)))

        tile_y = TILE_TOP + self.row_index * TILE_H
        self.rect.x = start_x
        self.rect.y = tile_y + TILE_H - self.rect.height

        self.bg = bg
        self.speed = self.BASE_SPEED
        self.hp = self.MAX_HP

        now = pygame.time.get_ticks()
        self.animation_timer = now
        self.last_attack_time = now

        self.attack_target_id = None
        self.attack_target = None

        self.death_started_at = None
        self.ready_to_remove = False

    # -------------------- 状态 / 动画 --------------------

    def set_animation(self, state: str):
        if state == self.state:
            return
        if state in self.animations:
            self.state = state
            self.frames = self.animations[state]
            self.frame_index = 0
            self.image = self.frames[self.frame_index]

            if self.state == "attack":
                self._cached_speed = getattr(self, "_cached_speed", self.speed)
                self.speed = 0
            elif self.state == "walk":
                self.speed = getattr(self, "_cached_speed", self.BASE_SPEED)

    def _advance_frame(self, now: int):
        if now - self.animation_timer >= self.ANIM_INTERVAL:
            self.animation_timer = now
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]

    # -------------------- 主循环更新 --------------------

    def update(self):
        now = pygame.time.get_ticks()
        self._advance_frame(now)

        if self.state == "dead":
            if self.death_started_at and now - self.death_started_at >= self.DEAD_REMOVE_DELAY:
                self.ready_to_remove = True
            return

        if self.attack_target_id:
            p = self.engine.AllPlants.get(self.attack_target_id)
            if (not p) or p.get("health", 0) <= 0:
                self.attack_target_id = None
                self.attack_target = None
                self.set_animation("walk")

        if self.state == "walk":
            self.rect.x -= self.speed
            self._try_lock_target()

        if self.state == "attack":
            self.perform_attack()

        if self.rect.right < 0:
            self.ready_to_remove = True

        if self.hp <= 0 and self.state != "dead":
            self.set_animation("dead")
            self.death_started_at = now

    # -------------------- 碰撞/锁定与攻击 --------------------

    def _try_lock_target(self):
        if not self.engine:
            return
        row = self.row_index
        nearest_pid = None
        for col in range(8, -1, -1):
            pid = self.engine.Grid[row][col]
            if not pid:
                continue
            cell_rect = pygame.Rect(
                TILE_LEFT + col * TILE_W,
                TILE_TOP + row * TILE_H,
                TILE_W,
                TILE_H
            )
            if (self.rect.left <= cell_rect.right - self.CONTACT_PAD and
                self.rect.right > cell_rect.left + 4):
                nearest_pid = pid
                break

        if nearest_pid:
            self.attack_target_id = nearest_pid
            self.attack_target = self.engine.AllPlants.get(nearest_pid)
            self.set_animation("attack")

    def perform_attack(self):
        if not self.attack_target or not self.attack_target_id:
            return
        now = pygame.time.get_ticks()
        if now - self.last_attack_time >= self.ATTACK_INTERVAL:
            self.last_attack_time = now
            hp = max(0, self.attack_target.get("health", 0) - self.ATTACK_DAMAGE)
            self.attack_target["health"] = hp
            if hp <= 0:
                self.attack_target = None
                self.attack_target_id = None
                self.set_animation("walk")
