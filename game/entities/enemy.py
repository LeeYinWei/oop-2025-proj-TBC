import pygame
import math
import sys, os
import random

# 如果需要使用 BOTTOM_Y
from game.constants import BOTTOM_Y

# 如果需要用 load_config
from game.config_loader import load_config

from game.entities.gaseffect import GasEffect
from game.entities.electriceffect import ElectricEffect
from game.entities.smokeeffect import SmokeEffect
from game.entities.shockwaveeffect import ShockwaveEffect
from game.entities.physiceffect import PhysicEffect
from game.entities.soul import Soul
from game.constants import smoke_images, electric_images, gas_images, physic_images

class Enemy:
    def __init__(self, x, y, hp, speed, color, attack_range=50, is_aoe=False, is_boss=False,
                is_b=False, atk=10, kb_limit=1, width=50, height=50, idle_frames=None,
                move_frames=None, windup_frames=None, attack_frames=None, recovery_frames=None,
                kb_frames=None, windup_duration=200, attack_duration=100, recovery_duration=50,
                attack_interval=1000, hp_multiplier=1.0, atk_multiplier=1.0, done_attack=False, 
                reward = 5, attack_type="gun"):
        self.x = x
        self.y = y-height
        self.y0 = y-height  # 儲存原始 y 座標以便恢復
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
            "idle": 600, "moving": 600,
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
        self.physic_effects = []  # 儲存物理特效實例
        self.electric_effects = []  # 儲存電擊特效實例
        self.gas_effects = []
        self.done_attack = done_attack
        self.slot_index = None  # 儲存使用的 y_slot 索引
        self.reward = reward
        self.attack_type = attack_type  # 攻擊類型，預設為 "gun"

    def move(self):
        if not self.is_attacking and not self.kb_animation and self.anim_state not in ["windup", "attacking", "recovery"]:
            self.x += self.speed
            self.is_attacking = False
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

    def take_damage(self, damage, attack_type):
        """處理受到傷害的邏輯，並根據攻擊類型生成特效"""
        self.hp -= damage
        if self.hp > 0:
            if attack_type == "gun":
                # 被攻擊時生成煙霧特效，3-5 個粒子，位置在角色中心
                center_x = self.x + self.width // 2
                center_y = self.y + self.height // 2
                for _ in range(random.randint(3, 5)):
                    smoke_x = center_x + random.randint(-5, 5)  # 小範圍隨機偏移
                    smoke_y = center_y + random.randint(-5, 5)  # 小範圍隨機偏移
                    self.smoke_effects.append(SmokeEffect(smoke_x, smoke_y, smoke_images))
            elif attack_type == "physic":
                # 被攻擊時生成物理特效，3-5 個粒子，位置在角色中心
                center_x = self.x + self.width // 2
                center_y = self.y + self.height // 2
                for _ in range(random.randint(3, 5)):
                    physic_x = center_x + random.randint(-5, 5)
                    physic_y = center_y + random.randint(-5, 5)
                    self.physic_effects.append(PhysicEffect(physic_x, physic_y, physic_images))
            elif attack_type == "electric": 
                # 被攻擊時生成電擊特效，3-5 個粒子，位置在角色中心
                center_x = self.x + self.width // 2
                center_y = self.y + self.height // 2
                for _ in range(random.randint(3, 5)):
                    electric_x = center_x + random.randint(-5, 5)
                    electric_y = center_y + random.randint(-5, 5)
                    self.electric_effects.append(ElectricEffect(electric_x, electric_y, electric_images))
            elif attack_type == "gas":
                # 被攻擊時生成氣體特效，3-5 個粒子，位置在角色中心
                center_x = self.x + self.width // 2
                center_y = self.y + self.height // 2
                for _ in range(random.randint(3, 5)):
                    gas_x = center_x + random.randint(-5, 5)
                    gas_y = center_y + random.randint(-5, 5)
                    self.gas_effects.append(GasEffect(gas_x, gas_y, gas_images))
        thresholds_crossed = int(self.last_hp / self.kb_threshold) - int(self.hp / self.kb_threshold)
        if thresholds_crossed > 0:
            self.knock_back()
        self.last_hp = self.hp
        #print(f"(In take_damage)Enemy took damage: {damage}, remaining HP: {self.hp}")

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
                self.is_attacking = False
                self.done_attack = False
                self.y = self.y0  # 恢復到原始 y 座標
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

    def update_physic_effects(self):
        self.physic_effects = [physic for physic in self.physic_effects if physic.update()]

    def update_electric_effects(self):
        self.electric_effects = [electric for electric in self.electric_effects if electric.update()]
    
    def update_gas_effects(self):
        self.gas_effects = [gas for gas in self.gas_effects if gas.update()]

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
        #self.draw_hp_bar(screen)
        # 繪製煙霧特效
        for smoke in self.smoke_effects:
            smoke.draw(screen)
        # 繪製物理特效
        for physic in self.physic_effects:
            physic.draw(screen)
        
        # 繪製電擊特效
        for electric in self.electric_effects:
            electric.draw(screen)

        # 繪製氣體特效
        for gas in self.gas_effects:
            gas.draw(screen)
        if self.is_boss:
            boss_label = pygame.font.SysFont(None, 20).render("Boss", True, (255, 0, 0))
            screen.blit(boss_label, (self.x, self.y - 20))

    def draw_hp_bar(self, screen):
        bar_width = self.width
        bar_height = 5
        fill = max(0, self.hp / self.max_hp) * bar_width
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y - 10, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 10, fill, bar_height))
        pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y - 10, bar_width, bar_height), 1)

    def get_attack_zone(self):
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