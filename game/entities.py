import pygame
import math
import sys, os
import random

from .config_loader import load_config

# Constants
BOTTOM_Y = 490

class Soul:
    def __init__(self, x, y, radius=10, duration=1000):
        self.x = x
        self.y = y
        self.radius = radius
        self.start_time = pygame.time.get_ticks()
        self.duration = duration
        self.alpha = 1.0
        self.color = (255, 255, 255)  # 白色圓形

    def update(self):
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time
        if elapsed >= self.duration:
            return False
        self.y -= 0.5  # 上升動畫
        self.alpha = max(0, 1.0 - (elapsed / self.duration))  # 透明度漸變
        return True

    def draw(self, screen):
        if self.alpha > 0:
            soul_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                soul_surface,
                (self.color[0], self.color[1], self.color[2], int(self.alpha * 255)),
                (self.radius, self.radius),
                self.radius
            )
            screen.blit(soul_surface, (self.x - self.radius, self.y - self.radius))

class ShockwaveEffect:
    def __init__(self, x, y, max_radius=200, duration=1000, thickness=5):
        self.x = x
        self.y = y
        self.start_time = pygame.time.get_ticks()
        self.duration = duration
        self.alpha = 1.0
        self.max_radius = max_radius
        self.thickness = thickness  # 中空圓形的邊框厚度

    def update(self):
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time
        if elapsed >= self.duration:
            return False
        self.alpha = max(0, 1.0 - (elapsed / self.duration))
        return True

    def draw(self, screen):
        if self.alpha > 0:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.start_time
            progress = elapsed / self.duration
            radius = int(self.max_radius * progress)
            if radius > self.thickness:  # 確保內徑大於 0
                inner_radius = max(0, radius - self.thickness)
                outer_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(outer_surface, (100, 100, 255, int(self.alpha * 255)), (radius, radius), radius, self.thickness)
                screen.blit(outer_surface, (self.x - radius, self.y - radius))

class SmokeEffect:
    def __init__(self, x, y, duration=1000):
        self.x = x
        self.y = y
        self.start_time = pygame.time.get_ticks()
        self.duration = duration  # 煙霧持續時間
        self.alpha = 1.0
        self.size = random.randint(20, 40)  # 隨機煙霧大小
        self.color = (150, 150, 150)  # 灰色煙霧

    def update(self):
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time
        if elapsed >= self.duration:
            return False
        self.alpha = max(0, 1.0 - (elapsed / self.duration))  # 逐漸消失
        self.size += 0.5  # 煙霧逐漸擴散
        self.y -= 0.3  # 向上飄動
        return True

    def draw(self, screen):
        if self.alpha > 0:
            smoke_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                smoke_surface,
                (self.color[0], self.color[1], self.color[2], int(self.alpha * 255)),
                (self.size, self.size),
                self.size
            )
            screen.blit(smoke_surface, (self.x - self.size, self.y - self.size))

# ... (前面的代碼保持不變)

class Cat:
    def __init__(self, x, y, hp, atk, speed, color, attack_range=50, is_aoe=False,
                 width=50, height=50, kb_limit=1, idle_frames=None, move_frames=None,
                 windup_frames=None, attack_frames=None, recovery_frames=None,
                 kb_frames=None, windup_duration=200, attack_duration=100, recovery_duration=50,
                 target_attributes=None, immunities=None, boosts=None, status_effects_config=None, attack_interval=1000, done_attack=False):
        self.x = x
        self.y = BOTTOM_Y - height
        self.hp = hp
        self.max_hp = hp
        self.atk = atk
        self.speed = speed
        self.color = color
        self.attack_range = attack_range
        self.is_aoe = is_aoe
        self.width = width
        self.height = height
        self.kb_limit = kb_limit
        self.kb_count = 0
        self.kb_threshold = self.max_hp / self.kb_limit if self.kb_limit > 0 else self.max_hp
        self.last_hp = hp
        self.last_attack_time = 0
        self.is_attacking = False
        self.contact_points = []
        self.anim_state = "idle"
        self.anim_progress = 0
        self.anim_frame = 0
        self.anim_start_time = 0
        self.anim_frames = {
            "idle": [], "moving": [], "windup": [], "attacking": [], "recovery": [], "knockback": []
        }
        self.frame_durations = {
            "idle": 600, "moving": 100,
            "windup": windup_duration / max(1, len(windup_frames or [])),
            "attacking": attack_duration / max(1, len(attack_frames or [])),
            "recovery": recovery_duration / max(1, len(recovery_frames or [])),
            "knockback": 100
        }
        for state, frames in [
            ("idle", idle_frames), ("moving", move_frames), ("windup", windup_frames),
            ("attacking", attack_frames), ("recovery", recovery_frames), ("knockback", kb_frames)
        ]:
            if frames:
                for frame_path in frames:
                    try:
                        img = pygame.image.load(frame_path)
                        img = pygame.transform.scale(img, (self.width, self.height))
                        self.anim_frames[state].append(img)
                    except pygame.error as e:
                        print(f"Cannot load frame '{frame_path}': {e}")
        self.fallback_image = None
        if not self.anim_frames["idle"]:
            self.fallback_image = pygame.Surface((self.width, self.height))
            self.fallback_image.fill(color)
            self.anim_frames["idle"] = [self.fallback_image]
        self.kb_animation = False
        self.kb_start_x = 0
        self.kb_target_x = 0
        self.kb_start_y = self.y
        self.kb_progress = 0
        self.kb_duration = 500  # 將後退時間從 2000ms 改為 500ms
        self.kb_start_time = 0
        self.kb_rotation = 0
        self.target_attributes = target_attributes if target_attributes is not None else []
        self.immunities = immunities if immunities is not None else {}
        self.boosts = boosts if boosts is not None else {}
        self.status_effects = {}
        self.status_effects_config = status_effects_config if status_effects_config is not None else {}
        self.attack_interval = attack_interval
        self.has_retreated = False  # 添加後退標記，預設為 False
        self.smoke_effects = []  # 儲存煙霧特效實例

        self.done_attack = done_attack

    def move(self):
        if not self.is_attacking and not self.kb_animation and self.anim_state not in ["windup", "attacking", "recovery"]:
            self.x -= self.speed
            self.is_attacking = False
            self.anim_state = "moving"

    def knock_back(self):
        if "Knockback Immunity" not in self.immunities.get("self", []):
            self.kb_animation = True
            self.kb_start_x = self.x
            self.kb_target_x = self.x + 50
            self.kb_start_y = self.y
            self.kb_start_time = pygame.time.get_ticks()
            self.kb_progress = 0
            self.anim_state = "moving"
            self.kb_count += 1
            if self.kb_count >= self.kb_limit:
                self.hp = 0

    def start_retreat(self, distance):
        if not self.is_attacking and not self.has_retreated:
            self.kb_animation = True
            self.kb_start_x = self.x
            self.kb_target_x = self.x + distance  # 向左移動指定距離
            self.kb_start_y = self.y
            self.kb_start_time = pygame.time.get_ticks()
            self.kb_progress = 0
            self.anim_state = "moving"
            self.has_retreated = True

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp > 0:
            # 被攻擊時生成煙霧特效，3-5 個粒子，位置在角色中心
            center_x = self.x + self.width // 2
            center_y = self.y + self.height // 2
            for _ in range(random.randint(3, 5)):
                smoke_x = center_x + random.randint(-5, 5)  # 小範圍隨機偏移
                smoke_y = center_y + random.randint(-5, 5)  # 小範圍隨機偏移
                self.smoke_effects.append(SmokeEffect(smoke_x, smoke_y))
        thresholds_crossed = int(self.last_hp / self.kb_threshold) - int(self.hp / self.kb_threshold)
        if thresholds_crossed > 0:
            self.knock_back()
        self.last_hp = self.hp

    def update_animation(self):
        current_time = pygame.time.get_ticks()
        if self.kb_animation:
            elapsed = current_time - self.kb_start_time
            self.kb_progress = min(elapsed / self.kb_duration, 1.0)
            # eased_progress = self.kb_progress ** 2  # 可選移除平滑效果
            eased_progress = self.kb_progress  # 改為線性移動以提高感知速度
            self.x = self.kb_start_x + (self.kb_target_x - self.kb_start_x) * eased_progress
            self.y = self.kb_start_y
            if self.kb_progress < 0.5:
                self.kb_rotation = 20 * self.kb_progress
            else:
                self.kb_rotation = 20 * (1 - self.kb_progress)
            if self.kb_progress >= 1.0:
                self.kb_animation = False
                self.anim_state = "idle"
                self.is_attacking = False
                self.done_attack = False
                self.y = BOTTOM_Y - self.height
                self.kb_rotation = 0
        else:
            if self.anim_state in ["windup", "attacking", "recovery"]:
                elapsed = current_time - self.anim_start_time
                state_duration = (
                    self.frame_durations["windup"] * len(self.anim_frames["windup"]) if self.anim_state == "windup" else
                    self.frame_durations["attacking"] * len(self.anim_frames["attacking"]) if self.anim_state == "attacking" else
                    self.frame_durations["recovery"] * len(self.anim_frames["recovery"])
                )
                if elapsed >= state_duration:
                    if self.anim_state == "windup":
                        self.anim_state = "attacking"
                        self.anim_start_time = current_time
                    elif self.anim_state == "attacking":
                        self.anim_state = "recovery"
                        self.anim_start_time = current_time
                    elif self.anim_state == "recovery":
                        self.anim_state = "idle"
                        self.anim_start_time = current_time
                        self.is_attacking = False
                        self.done_attack = False  # 攻擊完成後重置
                self.anim_progress = min(elapsed / state_duration, 1.0) if state_duration > 0 else 0
            elif not self.is_attacking and self.anim_state != "moving":
                self.anim_state = "idle"
                self.anim_progress = (current_time / self.frame_durations["idle"]) % 1
            elif self.anim_state == "moving":
                self.anim_progress = (current_time / self.frame_durations["moving"]) % 1

    def update_smoke_effects(self):
        self.smoke_effects = [smoke for smoke in self.smoke_effects if smoke.update()]

    def get_current_frame(self):
        state = "moving" if self.kb_animation else self.anim_state
        frames = self.anim_frames[state]
        if not frames:
            frames = self.anim_frames["idle"]
        frame_count = len(frames)
        if frame_count == 0:
            return self.fallback_image
        frame_index = int(self.anim_progress * frame_count) % frame_count
        return frames[frame_index]

    def draw(self, screen):
        self.update_animation()
        current_frame = self.get_current_frame()
        if current_frame:
            rotated_image = pygame.transform.rotate(current_frame, -self.kb_rotation)
            rect = rotated_image.get_rect(center=(self.x + self.width / 2, self.y + self.height / 2))
            screen.blit(rotated_image, rect.topleft)
        self.draw_hp_bar(screen)
        # 繪製煙霧特效
        for smoke in self.smoke_effects:
            smoke.draw(screen)

    def draw_hp_bar(self, screen):
        bar_width = self.width
        bar_height = 5
        fill = max(0, self.hp / self.max_hp) * bar_width
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y - 10, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 10, fill, bar_height))

    def get_attack_zone(self):
        return pygame.Rect(self.x - self.attack_range, self.y, self.attack_range, self.height)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def apply_status_effect(self, effect, duration, chance=0.3, target=None):
        """應用狀態效果到目標，考慮機率和免疫"""
        if not target or pygame.time.get_ticks() % 100 < chance * 100:
            target_attrs = getattr(target, 'attributes', [])
            for attr in target_attrs:
                if effect in self.immunities.get(attr, []):
                    return
            if target:
                target.status_effects[effect] = pygame.time.get_ticks() + duration * 1000
                if effect == "Knockback":
                    target.knock_back()

    def update_status_effects(self, current_time):
        """更新自身狀態效果"""
        to_remove = []
        for effect, end_time in self.status_effects.items():
            if current_time >= end_time:
                to_remove.append(effect)
            elif effect == "Slow":
                self.speed *= 0.5
            elif effect == "Stun":
                self.anim_state = "idle"
                self.is_attacking = False
            elif effect == "Weaken":
                self.atk *= 0.7
            elif effect == "Curse":
                self.hp -= self.max_hp * 0.01
        for effect in to_remove:
            del self.status_effects[effect]
            if effect == "Slow":
                self.speed /= 0.5
            elif effect == "Weaken":
                self.atk /= 0.7

# ... (後面的 Enemy, Tower, Level 類保持不變)
class Enemy:
    def __init__(self, x, y, hp, speed, color, attack_range=50, is_aoe=False, is_boss=False,
                is_b=False, atk=10, kb_limit=1, width=50, height=50, idle_frames=None,
                move_frames=None, windup_frames=None, attack_frames=None, recovery_frames=None,
                kb_frames=None, windup_duration=200, attack_duration=100, recovery_duration=50,
                attack_interval=1000, hp_multiplier=1.0, atk_multiplier=1.0):
        self.x = x
        self.y = BOTTOM_Y - height
        self.hp = int(hp * hp_multiplier)  # Use variant-specific multiplier
        self.max_hp = self.hp
        self.atk = atk * atk_multiplier  # Use variant-specific multiplier
        self.speed = speed
        self.color = color
        self.attack_range = attack_range
        self.is_aoe = is_aoe
        self.is_boss = is_boss
        self.width = width
        self.height = height
        self.last_attack_time = 0
        self.is_attacking = False
        self.contact_points = []
        self.kb_limit = kb_limit
        self.kb_count = 0
        self.kb_threshold = self.max_hp / self.kb_limit if self.kb_limit > 0 else self.max_hp
        self.last_hp = hp
        self.anim_state = "idle"
        self.anim_progress = 0
        self.anim_start_time = 0
        self.anim_frames = {
            "idle": [], "moving": [], "windup": [], "attacking": [], "recovery": [], "knockback": []
        }
        self.frame_durations = {
            "idle": 600, "moving": 100,
            "windup": windup_duration / max(1, len(windup_frames or [])),
            "attacking": attack_duration / max(1, len(attack_frames or [])),
            "recovery": recovery_duration / max(1, len(recovery_frames or [])),
            "knockback": 100
        }
        for state, frames in [
            ("idle", idle_frames), ("moving", move_frames), ("windup", windup_frames),
            ("attacking", attack_frames), ("recovery", recovery_frames), ("knockback", kb_frames)
        ]:
            if frames:
                for frame_path in frames:
                    try:
                        img = pygame.image.load(frame_path)
                        img = pygame.transform.scale(img, (self.width, self.height))
                        self.anim_frames[state].append(img)
                    except pygame.error as e:
                        print(f"Cannot load frame '{frame_path}': {e}")
        self.fallback_image = None
        if not self.anim_frames["idle"]:
            self.fallback_image = pygame.Surface((self.width, self.height))
            self.fallback_image.fill(color)
            self.anim_frames["idle"] = [self.fallback_image]
        self.kb_animation = False
        self.kb_start_x = 0
        self.kb_target_x = 0
        self.kb_start_y = self.y
        self.kb_progress = 0
        self.kb_duration = 300
        self.kb_start_time = 0
        self.kb_rotation = 0
        self.status_effects = {}
        self.status_effects_config = {}
        self.attack_interval = attack_interval
        self.smoke_effects = []  # 儲存煙霧特效實例

    def move(self):
        if not self.is_attacking and not self.kb_animation and self.anim_state not in ["windup", "attacking", "recovery"]:
            self.x += self.speed
            self.anim_state = "moving"

    def knock_back(self):
        self.kb_animation = True
        self.kb_start_x = self.x
        self.kb_target_x = self.x - 50  # 向後跳
        self.kb_start_y = self.y
        self.kb_start_time = pygame.time.get_ticks()
        self.kb_progress = 0
        self.anim_state = "knockback"
        self.kb_count += 1
        if self.kb_count >= self.kb_limit:
            self.hp = 0

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp > 0:
            # 被攻擊時生成煙霧特效，3-5 個粒子，位置在角色中心
            center_x = self.x + self.width // 2
            center_y = self.y + self.height // 2
            for _ in range(random.randint(3, 5)):
                smoke_x = center_x + random.randint(-5, 5)  # 小範圍隨機偏移
                smoke_y = center_y + random.randint(-5, 5)  # 小範圍隨機偏移
                self.smoke_effects.append(SmokeEffect(smoke_x, smoke_y))
        thresholds_crossed = int(self.last_hp / self.kb_threshold) - int(self.hp / self.kb_threshold)
        if thresholds_crossed > 0:
            self.knock_back()
        self.last_hp = self.hp

    def update_animation(self):
        current_time = pygame.time.get_ticks()
        if self.kb_animation:
            elapsed = current_time - self.kb_start_time
            self.kb_progress = min(elapsed / self.kb_duration, 1.0)
            eased_progress = 1 - (1 - self.kb_progress) ** 2
            self.x = self.kb_start_x + (self.kb_target_x - self.kb_start_x) * eased_progress
            self.y = self.kb_start_y
            if self.kb_progress < 0.5:
                self.kb_rotation = 20 * self.kb_progress
            else:
                self.kb_rotation = 20 * (1 - self.kb_progress)
            if self.kb_progress >= 1.0:
                self.kb_animation = False
                self.anim_state = "idle"
                self.y = BOTTOM_Y - self.height
                self.kb_rotation = 0
        else:
            if self.anim_state in ["windup", "attacking", "recovery"]:
                elapsed = current_time - self.anim_start_time
                state_duration = (
                    self.frame_durations["windup"] * len(self.anim_frames["windup"]) if self.anim_state == "windup" else
                    self.frame_durations["attacking"] * len(self.anim_frames["attacking"]) if self.anim_state == "attacking" else
                    self.frame_durations["recovery"] * len(self.anim_frames["recovery"])
                )
                if elapsed >= state_duration:
                    if self.anim_state == "windup":
                        self.anim_state = "attacking"
                        self.anim_start_time = current_time
                    elif self.anim_state == "attacking":
                        self.anim_state = "recovery"
                        self.anim_start_time = current_time
                    elif self.anim_state == "recovery":
                        self.anim_state = "idle"
                        self.anim_start_time = current_time
                        self.is_attacking = False
                self.anim_progress = min(elapsed / state_duration, 1.0) if state_duration > 0 else 0
            elif not self.is_attacking and self.anim_state != "moving":
                self.anim_state = "idle"
                self.anim_progress = (current_time / self.frame_durations["idle"]) % 1
            elif self.anim_state == "moving":
                self.anim_progress = (current_time / self.frame_durations["moving"]) % 1

    def update_smoke_effects(self):
        self.smoke_effects = [smoke for smoke in self.smoke_effects if smoke.update()]

    def get_current_frame(self):
        state = "knockback" if self.kb_animation else self.anim_state
        frames = self.anim_frames[state]
        if not frames:
            frames = self.anim_frames["idle"]
        frame_count = len(frames)
        if frame_count == 0:
            return self.fallback_image
        frame_index = int(self.anim_progress * frame_count) % frame_count
        return frames[frame_index]

    def draw(self, screen):
        self.update_animation()
        current_frame = self.get_current_frame()
        if current_frame:
            rotated_image = pygame.transform.rotate(current_frame, self.kb_rotation)
            rect = rotated_image.get_rect(center=(self.x + self.width / 2, self.y + self.height / 2))
            screen.blit(rotated_image, rect.topleft)
        self.draw_hp_bar(screen)
        # 繪製煙霧特效
        for smoke in self.smoke_effects:
            smoke.draw(screen)
        if self.is_boss:
            boss_label = pygame.font.SysFont(None, 20).render("Boss", True, (255, 0, 0))
            screen.blit(boss_label, (self.x, self.y - 20))

    def draw_hp_bar(self, screen):
        bar_width = self.width
        bar_height = 5
        fill = max(0, self.hp / self.max_hp) * bar_width
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y - 10, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 10, fill, bar_height))

    def get_attack_zone(self):
        if self.kb_animation or self.anim_state in ["windup", "recovery"]:
            return pygame.Rect(0, 0, 0, 0)
        return pygame.Rect(self.x + self.width, self.y, self.attack_range, self.height)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update_status_effects(self, current_time):
        """更新狀態效果"""
        to_remove = []
        for effect, end_time in self.status_effects.items():
            if current_time >= end_time:
                to_remove.append(effect)
            elif effect == "Slow":
                self.speed *= 0.5
            elif effect == "Stun":
                self.anim_state = "idle"
                self.is_attacking = False
            elif effect == "Weaken":
                self.atk *= 0.7
            elif effect == "Curse":
                self.hp -= self.max_hp * 0.01
        for effect in to_remove:
            del self.status_effects[effect]
            if effect == "Slow":
                self.speed /= 0.5
            elif effect == "Weaken":
                self.atk /= 0.7

class Tower:
    def __init__(self, x, y, hp, color=(100, 100, 255), tower_path=None, width=120, height=400, is_enemy=False):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = hp
        self.color = color
        self.tower_path = tower_path
        self.width = width
        self.height = height
        self.last_attack_time = 0
        self.is_attacking = False
        self.contact_points = []
        self.is_enemy = is_enemy
        self.image = None
        if is_enemy and tower_path:
            try:
                self.image = pygame.image.load(tower_path)
                self.image = pygame.transform.scale(self.image, (self.width, self.height))
            except pygame.error as e:
                print(f"Cannot load tower image '{tower_path}': {e}")
                pygame.quit()
                sys.exit()
        elif tower_path:
            try:
                self.image = pygame.image.load(tower_path)
                self.image = pygame.transform.scale(self.image, (self.width, self.height))
            except pygame.error as e:
                print(f"Cannot load tower image '{tower_path}': {e}")

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.x, self.y))
        else:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        self.draw_hp_bar(screen)

    def draw_hp_bar(self, screen):
        bar_width = self.width
        bar_height = 5
        fill = max(0, self.hp / self.max_hp) * bar_width
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y - 10, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 10, fill, bar_height))

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, int(self.height))

class Level:
    def __init__(self, name, enemy_types, spawn_interval, survival_time, background_path, our_tower_config, enemy_tower_config, tower_distance):
        self.name = name
        self.enemy_configs = {et["type"]: load_config("enemy_folder", et["type"]) for et in enemy_types}
        valid_attributes = {"紅", "黑", "天", "鐵", "異", "惡", "死", "古", "無"}
        self.enemy_types = []
        for et in enemy_types:
            et_copy = et.copy()
            enemy_type = et_copy["type"]
            config = self.enemy_configs.get(enemy_type, {})
            et_copy["attributes"] = config.get("attributes", [])
            et_copy["attributes"] = list(dict.fromkeys([attr for attr in et_copy["attributes"] if attr in valid_attributes]))
            self.enemy_types.append(et_copy)
        self.spawn_interval = spawn_interval
        self.survival_time = survival_time
        self.spawned_counts = {(et["type"], et.get("variant", "default")): 0 for et in self.enemy_types}
        self.all_limited_spawned = False
        self.background = None
        try:
            self.background = pygame.image.load(background_path)
            self.background = pygame.transform.scale(self.background, (1280, 600))
        except pygame.error as e:
            print(f"Cannot load background image '{background_path}': {e}")
            pygame.quit()
            sys.exit()
        self.last_spawn_times = {(et["type"], et.get("variant", "default")): -et.get("initial_delay", 0) for et in self.enemy_types}
        self.our_tower_config = our_tower_config
        self.enemy_tower_config = enemy_tower_config
        self.tower_distance = tower_distance
        self.reset_towers()

    def reset_towers(self):
        SCREEN_WIDTH = 1280
        CENTER_X = SCREEN_WIDTH / 2
        our_tower_width = self.our_tower_config["width"]
        enemy_tower_width = self.enemy_tower_config["width"]
        tower_distance = self.tower_distance

        our_tower_center = CENTER_X + tower_distance / 2
        enemy_tower_center = CENTER_X - tower_distance / 2
        our_tower_x = our_tower_center - our_tower_width / 2
        enemy_tower_x = enemy_tower_center - enemy_tower_width / 2

        self.our_tower = Tower(
            x=our_tower_x,
            y=self.our_tower_config["y"],
            hp=self.our_tower_config["hp"],
            color=self.our_tower_config.get("color", (100, 100, 255)),
            tower_path=self.our_tower_config.get("tower_path"),
            width=our_tower_width,
            height=self.our_tower_config["height"]
        )
        self.enemy_tower = Tower(
            x=enemy_tower_x,
            y=self.enemy_tower_config["y"],
            hp=self.enemy_tower_config["hp"],
            tower_path=self.enemy_tower_config["tower_path"],
            width=enemy_tower_width,
            height=self.enemy_tower_config["height"],
            is_enemy=True
        )

    def check_all_limited_spawned(self):
        """Check if all limited enemies have been spawned."""
        for enemy_type in self.enemy_types:
            if enemy_type.get("is_limited", False):
                key = (enemy_type["type"], enemy_type.get("variant", "default"))
                spawn_count = enemy_type.get("spawn_count", 0)
                if spawn_count > 0 and self.spawned_counts[key] < spawn_count:
                    return False
        return True

# 更新 cat_types 載入邏輯
cat_types = {}
cat_cooldowns = {}
cat_costs = {}
cat_folder = "cat_folder"
if os.path.exists(cat_folder):
    for cat_type in os.listdir(cat_folder):
        if os.path.isdir(os.path.join(cat_folder, cat_type)):
            try:
                config = load_config(cat_folder, cat_type)
                cat_types[cat_type] = lambda x, y, cfg=config: Cat(
                    x, y, cfg["hp"], cfg["atk"], cfg["speed"], cfg["color"],
                    cfg["attack_range"], cfg["is_aoe"], cfg["width"], cfg["height"],
                    cfg["kb_limit"], cfg.get("idle_frames"), cfg.get("move_frames"),
                    cfg.get("windup_frames"), cfg.get("attack_frames"), cfg.get("recovery_frames"),
                    cfg.get("kb_frames"), cfg["windup_duration"], cfg["attack_duration"],
                    cfg["recovery_duration"],
                    target_attributes=cfg.get("target_attributes", []),
                    immunities=cfg.get("immunities", {}),
                    boosts=cfg.get("boosts", {}),
                    status_effects_config=cfg.get("status_effects", {}),
                    attack_interval=cfg.get("attack_interval", 1000)
                )
                cat_cooldowns[cat_type] = config["cooldown"]
                cat_costs[cat_type] = config["cost"]
            except Exception as e:
                print(f"Error loading cat config for '{cat_type}': {e}")
else:
    print(f"Directory '{cat_folder}' not found")
    sys.exit()

# 同樣更新 enemy_types 載入邏輯
enemy_types = {}
enemy_folder = "enemy_folder"
if os.path.exists(enemy_folder):
    for enemy_type in os.listdir(enemy_folder):
        if os.path.isdir(os.path.join(enemy_folder, enemy_type)):
            try:
                config = load_config(enemy_folder, enemy_type)
                enemy_types[enemy_type] = lambda x, y, is_b, cfg=config: Enemy(
                    x, y, cfg["hp"], cfg["speed"], cfg["color"], cfg["attack_range"], cfg["is_aoe"],
                    is_boss=cfg.get("is_boss", False), is_b=is_b, atk=cfg["atk"], kb_limit=cfg["kb_limit"],
                    width=cfg["width"], height=cfg["height"],
                    idle_frames=cfg.get("idle_frames"), move_frames=cfg.get("move_frames"),
                    windup_frames=cfg.get("windup_frames"), attack_frames=cfg.get("attack_frames"),
                    recovery_frames=cfg.get("recovery_frames"), kb_frames=cfg.get("kb_frames"),
                    windup_duration=cfg["windup_duration"], attack_duration=cfg["attack_duration"],
                    recovery_duration=cfg["recovery_duration"],
                    attack_interval=cfg.get("attack_interval", 1000),
                    hp_multiplier=cfg.get("hp_multiplier", 1.0),  # Default to 1.0 if not set
                    atk_multiplier=cfg.get("atk_multiplier", 1.0)  # Default to 1.0 if not set
                )
            except Exception as e:
                print(f"Error loading enemy config for '{enemy_type}': {e}")
else:
    print(f"Directory '{enemy_folder}' not found")
    sys.exit()

# Load configurations for levels (unchanged)
levels = []
level_folder = "level_folder"
if os.path.exists(level_folder):
    for level_subfolder in os.listdir(level_folder):
        if os.path.isdir(os.path.join(level_folder, level_subfolder)):
            try:
                config = load_config(level_folder, level_subfolder)
                levels.append(Level(
                    config["name"],
                    config["enemy_types"],
                    config["spawn_interval"],
                    config["survival_time"],
                    config["background_path"],
                    config["our_tower"],
                    config["enemy_tower"],
                    config["tower_distance"]
                ))
            except Exception as e:
                print(f"Error loading level config for '{level_subfolder}': {e}")
else:
    print(f"Directory '{level_folder}' not found")
    sys.exit()

