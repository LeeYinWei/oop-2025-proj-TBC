import pygame
import random
from abc import ABC, abstractmethod

# 假設的模組導入
from game.entities.gaseffect import GasEffect
from game.entities.electriceffect import ElectricEffect
from game.entities.smokeeffect import SmokeEffect
from game.entities.physiceffect import PhysicEffect
from game.constants import smoke_images, electric_images, gas_images, physic_images

class Common(ABC):
    def __init__(self, x, y, hp, atk, speed, color, attack_range=50, is_aoe=False,
                 width=50, height=50, kb_limit=1, idle_frames=None, move_frames=None,
                 windup_frames=None, attack_frames=None, recovery_frames=None,
                 kb_frames=None, windup_duration=200, attack_duration=100, recovery_duration=50,
                 attack_interval=1000, attack_type="gun", attack_phases=None):
        self.x = x
        self.y = y - height
        self.y0 = y - height
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
        self.contact_points = []  # 實際接觸點
        self.anim_state = "idle"
        self.anim_progress = 0
        self.anim_frame = 0
        self.anim_start_time = 0
        self.current_phase = 0  # 當前攻擊階段
        self.phase_start_time = 0
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
        self.smoke_effects = []
        self.physic_effects = []
        self.electric_effects = []
        self.gas_effects = []
        self.done_attack = False
        self.slot_index = None
        self.attack_type = attack_type
        self.attack_phases = attack_phases or [{"range": attack_range, "duration": attack_duration}]  # 預設單段

    @abstractmethod
    def move(self):
        pass

    @abstractmethod
    def get_attack_zone(self):
        pass

    def knock_back(self, direction=-50):
        if not hasattr(self, 'immunities') or "Knockback Immunity" not in self.immunities.get("self", []):
            self.kb_animation = True
            self.kb_start_x = self.x
            self.kb_target_x = self.x + direction
            self.kb_start_y = self.y
            self.kb_start_time = pygame.time.get_ticks()
            self.kb_progress = 0
            self.anim_state = "knockback"
            self.kb_count += 1
            if self.kb_count >= self.kb_limit:
                self.hp = 0

    def take_damage(self, damage, attack_type):
        self.hp -= damage
        if self.hp > 0:
            center_x = self.x + self.width // 2
            center_y = self.y + self.height // 2
            if attack_type == "gun":
                for _ in range(random.randint(3, 5)):
                    self.smoke_effects.append(SmokeEffect(center_x + random.randint(-5, 5),
                                                         center_y + random.randint(-5, 5), smoke_images))
            elif attack_type == "physic":
                for _ in range(random.randint(3, 5)):
                    self.physic_effects.append(PhysicEffect(center_x + random.randint(-5, 5),
                                                           center_y + random.randint(-5, 5), physic_images))
            elif attack_type == "electric":
                for _ in range(random.randint(3, 5)):
                    self.electric_effects.append(ElectricEffect(center_x + random.randint(-5, 5),
                                                               center_y + random.randint(-5, 5), electric_images))
            elif attack_type == "gas":
                for _ in range(random.randint(3, 5)):
                    self.gas_effects.append(GasEffect(center_x + random.randint(-5, 5),
                                                     center_y + random.randint(-5, 5), gas_images))
        thresholds_crossed = min(self.max_hp // self.kb_threshold - 1, int(self.last_hp / self.kb_threshold)) - int(self.hp / self.kb_threshold)
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
                self.is_attacking = False
                self.done_attack = False
                self.y = self.y0
                self.kb_rotation = 0
        elif self.is_attacking and self.anim_state in ["windup", "attacking", "recovery"]:
            elapsed = current_time - self.phase_start_time
            total_duration = sum(phase["duration"] for phase in self.attack_phases)
            if elapsed >= total_duration + self.frame_durations["recovery"] * len(self.anim_frames["recovery"]):
                self.anim_state = "idle"
                self.is_attacking = False
                self.done_attack = False
                self.current_phase = 0
            elif self.anim_state == "windup":
                if elapsed >= self.frame_durations["windup"] * len(self.anim_frames["windup"]):
                    self.anim_state = "attacking"
                    self.phase_start_time = current_time
            elif self.anim_state == "attacking":
                phase_duration = self.attack_phases[self.current_phase]["duration"]
                if elapsed - self.phase_start_time >= phase_duration:
                    self.current_phase += 1
                    if self.current_phase >= len(self.attack_phases):
                        self.anim_state = "recovery"
                        self.phase_start_time = current_time
                    else:
                        self.phase_start_time = current_time
            self.anim_progress = min(elapsed / total_duration, 1.0) if total_duration > 0 else 0
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
        self.draw_hp_bar(screen)
        for smoke in self.smoke_effects:
            smoke.draw(screen)
        for physic in self.physic_effects:
            physic.draw(screen)
        for electric in self.electric_effects:
            electric.draw(screen)
        for gas in self.gas_effects:
            gas.draw(screen)

    def draw_hp_bar(self, screen):
        bar_width = self.width
        bar_height = 5
        fill = max(0, self.hp / self.max_hp) * bar_width
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y - 10, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 10, fill, bar_height))
        pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y - 10, bar_width, bar_height), 1)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update_status_effects(self, current_time):
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



                