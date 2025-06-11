import asyncio
import platform
import pygame
import random
import sys
import os
import importlib.util
import math

# === Constants ===
BOTTOM_Y = 490

# === Load Configs from Folders ===
def load_config(folder, subfolder, config_name="config"):
    config_path = os.path.join(folder, subfolder, f"{config_name}.py")
    if not os.path.exists(config_path):
        print(f"Config file not found: {config_path}")
        sys.exit()
    spec = importlib.util.spec_from_file_location(config_name, config_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if folder == "level_folder":
        return module.level_config
    return module.cat_config if folder == "cat_folder" else module.enemy_config

# Load cat and enemy types from folders
cat_types = {}
cat_cooldowns = {}
cat_costs = {}
for cat_type in ["basic", "speedy", "tank"]:
    config = load_config("cat_folder", cat_type)
    cat_types[cat_type] = lambda x, y, cfg=config: Cat(
        x, y, cfg["hp"], cfg["atk"], cfg["speed"], cfg["color"],
        cfg["attack_range"], cfg["is_aoe"], cfg["width"], cfg["height"],
        cfg["kb_limit"], cfg["idle_frames"], cfg["move_frames"],
        cfg["windup_frames"], cfg["attack_frames"], cfg["recovery_frames"],
        cfg["kb_frames"], cfg["windup_duration"], cfg["attack_duration"],
        cfg["recovery_duration"]
    )
    cat_cooldowns[cat_type] = config["cooldown"]
    cat_costs[cat_type] = config["cost"]

# === Classes ===
class Soul:
    def __init__(self, x, y, width=20, height=20, duration=1000):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.start_time = pygame.time.get_ticks()
        self.duration = duration
        self.alpha = 1.0

    def update(self):
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time
        if elapsed >= self.duration:
            return False
        self.y -= 0.5
        self.alpha = max(0, 1.0 - (elapsed / self.duration))
        return True

    def draw(self, screen):
        if self.alpha > 0:
            soul_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.circle(
                soul_surface,
                (255, 255, 255, int(self.alpha * 255)),
                (self.width // 2, self.height // 2),
                self.width // 2
            )
            screen.blit(soul_surface, (self.x - self.width // 2, self.y - self.height // 2))

class Cat:
    def __init__(self, x, y, hp, atk, speed, color, attack_range=50, is_aoe=False,
                 width=50, height=50, kb_limit=1, idle_frames=None, move_frames=None,
                 windup_frames=None, attack_frames=None, recovery_frames=None,
                 kb_frames=None, windup_duration=200, attack_duration=100, recovery_duration=50):
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
            "idle": [],
            "moving": [],
            "windup": [],
            "attacking": [],
            "recovery": [],
            "knockback": []
        }
        self.frame_durations = {
            "idle": 100,
            "moving": 100,
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

    def move(self):
        if not self.is_attacking and not self.kb_animation and self.anim_state not in ["windup", "attacking", "recovery"]:
            self.x -= self.speed
            self.anim_state = "moving"

    def knock_back(self):
        self.kb_animation = True
        self.kb_start_x = self.x
        self.kb_target_x = self.x + 50
        self.kb_start_y = self.y
        self.kb_start_time = pygame.time.get_ticks()
        self.kb_progress = 0
        self.anim_state = "knockback"
        self.kb_count += 1
        if self.kb_count >= self.kb_limit:
            self.hp = 0

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
            rotated_image = pygame.transform.rotate(current_frame, -self.kb_rotation)
            rect = rotated_image.get_rect(center=(self.x + self.width / 2, self.y + self.height / 2))
            screen.blit(rotated_image, rect.topleft)
        self.draw_hp_bar(screen)

    def draw_hp_bar(self, screen):
        bar_width = self.width
        bar_height = 5
        fill = max(0, self.hp / self.max_hp) * bar_width
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y - 10, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 10, fill, bar_height))

    def get_attack_zone(self):
        if self.kb_animation or self.anim_state in ["windup", "recovery"]:
            return pygame.Rect(0, 0, 0, 0)
        return pygame.Rect(self.x - self.attack_range, self.y, self.attack_range, self.height)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Enemy:
    def __init__(self, x, y, hp, speed, color, attack_range=50, is_aoe=False, is_boss=False,
                 is_b=False, atk=10, kb_limit=1, width=50, height=50, idle_frames=None,
                 move_frames=None, windup_frames=None, attack_frames=None, recovery_frames=None,
                 kb_frames=None, windup_duration=200, attack_duration=100, recovery_duration=50):
        self.x = x
        self.y = BOTTOM_Y - height
        self.hp = hp * (2 if is_b else 1)
        self.max_hp = self.hp
        self.atk = atk * (1.5 if is_b else 1)
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
            "idle": [],
            "moving": [],
            "windup": [],
            "attacking": [],
            "recovery": [],
            "knockback": []
        }
        self.frame_durations = {
            "idle": 100,
            "moving": 100,
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

    def move(self):
        if not self.is_attacking and not self.kb_animation and self.anim_state not in ["windup", "attacking", "recovery"]:
            self.x += self.speed
            self.anim_state = "moving"

    def knock_back(self):
        self.kb_animation = True
        self.kb_start_x = self.x
        self.kb_target_x = self.x - 50
        self.kb_start_y = self.y
        self.kb_start_time = pygame.time.get_ticks()
        self.kb_progress = 0
        self.anim_state = "knockback"
        self.kb_count += 1
        if self.kb_count >= self.kb_limit:
            self.hp = 0

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
    def __init__(self, name, enemy_types, spawn_interval, survival_time, background_path, our_tower_config, enemy_tower_config):
        self.name = name
        self.enemy_types = enemy_types
        self.spawn_interval = spawn_interval
        self.survival_time = survival_time
        self.spawned_counts = {(et["type"], et.get("variant", "default")): 0 for et in enemy_types}
        self.all_limited_spawned = False
        self.background = None
        try:
            self.background = pygame.image.load(background_path)
            self.background = pygame.transform.scale(self.background, (1000, 600))
        except pygame.error as e:
            print(f"Cannot load background image '{background_path}': {e}")
            pygame.quit()
            sys.exit()
        self.last_spawn_times = {(et["type"], et.get("variant", "default")): -et.get("initial_delay", 0) for et in enemy_types}
        self.our_tower_config = our_tower_config
        self.enemy_tower_config = enemy_tower_config
        self.reset_towers()

    def reset_towers(self):
        self.our_tower = Tower(
            x=self.our_tower_config["x"],
            y=self.our_tower_config["y"],
            hp=self.our_tower_config["hp"],
            color=self.our_tower_config.get("color", (100, 100, 255)),
            tower_path=self.our_tower_config.get("tower_path"),
            width=self.our_tower_config["width"],
            height=self.our_tower_config["height"]
        )
        self.enemy_tower = Tower(
            x=self.enemy_tower_config["x"],
            y=self.enemy_tower_config["y"],
            hp=self.enemy_tower_config["hp"],
            tower_path=self.enemy_tower_config["tower_path"],
            width=self.enemy_tower_config["width"],
            height=self.enemy_tower_config["height"],
            is_enemy=True
        )

    def check_all_limited_spawned(self):
        for et in self.enemy_types:
            key = (et["type"], et.get("variant", "default"))
            if et["is_limited"] and self.spawned_counts[key] < et["spawn_count"]:
                return False
        return True

# Load levels from level_folder
levels = []
level_folders = ["level_1", "level_2", "level_3"]
for level_folder in level_folders:
    config = load_config("level_folder", level_folder)
    levels.append(Level(
        config["name"], config["enemy_types"], config["spawn_interval"], config["survival_time"],
        config["background_path"], config["our_tower"], config["enemy_tower"]
    ))

enemy_types = {}
for enemy_type in ["basic", "fast", "tank"]:
    config = load_config("enemy_folder", enemy_type)
    enemy_types[enemy_type] = lambda x, y, is_b, cfg=config: Enemy(
        x, y, cfg["hp"], cfg["speed"], cfg["color"], cfg["attack_range"], cfg["is_aoe"],
        is_boss=cfg.get("is_boss", False), is_b=is_b, atk=cfg["atk"], kb_limit=cfg["kb_limit"],
        width=cfg["width"], height=cfg["height"],
        idle_frames=cfg.get("idle_frames"), move_frames=cfg.get("move_frames"),
        windup_frames=cfg.get("windup_frames"), attack_frames=cfg.get("attack_frames"),
        recovery_frames=cfg.get("recovery_frames"), kb_frames=cfg.get("kb_frames"),
        windup_duration=cfg["windup_duration"], attack_duration=cfg["attack_duration"],
        recovery_duration=cfg["recovery_duration"]
    )

# === Battle Logic ===
def update_battle(cats, enemies, our_tower, enemy_tower, now, souls):
    for cat in cats:
        cat.is_attacking = False
        cat.contact_points = []
    for enemy in enemies:
        enemy.is_attacking = False
        enemy.contact_points = []
    our_tower.contact_points = []
    if enemy_tower:
        enemy_tower.contact_points = []

    for cat in cats:
        cat_attack_zone = cat.get_attack_zone()
        if cat.anim_state in ["windup", "attacking", "recovery"]:
            if cat.anim_state == "attacking" and now - cat.last_attack_time >= cat.frame_durations["attacking"] * len(cat.anim_frames["attacking"]):
                cat.last_attack_time = now
                if cat.is_aoe:
                    targets = [e for e in enemies if cat_attack_zone.colliderect(e.get_rect())]
                    if enemy_tower and cat_attack_zone.colliderect(enemy_tower.get_rect()):
                        targets.append(enemy_tower)
                    for tar in targets:
                        if isinstance(tar, Enemy):
                            e = tar
                            old_hp = e.hp
                            e.hp -= cat.atk
                            if e.hp > 0:
                                thresholds_crossed = int(old_hp / e.kb_threshold) - int(e.hp / e.kb_threshold)
                                if thresholds_crossed > 0:
                                    e.knock_back()
                            e.last_hp = e.hp
                            contact_rect = cat_attack_zone.clip(e.get_rect())
                            contact_point = contact_rect.center
                            e.contact_points.append(contact_point)
                            cat.contact_points.append(contact_point)
                        elif isinstance(tar, Tower):
                            tower = tar
                            tower.hp -= cat.atk
                            contact_rect = cat_attack_zone.clip(tower.get_rect())
                            contact_point = contact_rect.center
                            tower.contact_points.append(contact_point)
                            cat.contact_points.append(contact_point)
                else:
                    if enemy_tower and cat_attack_zone.colliderect(enemy_tower.get_rect()):
                        tower = enemy_tower
                        tower.hp -= cat.atk
                        contact_rect = cat_attack_zone.clip(tower.get_rect())
                        contact_point = contact_rect.center
                        tower.contact_points.append(contact_point)
                        cat.contact_points.append(contact_point)
                    else:
                        for enemy in enemies:
                            if cat_attack_zone.colliderect(enemy.get_rect()):
                                old_hp = enemy.hp
                                enemy.hp -= cat.atk
                                if enemy.hp > 0:
                                    thresholds_crossed = int(old_hp / enemy.kb_threshold) - int(enemy.hp / enemy.kb_threshold)
                                    if thresholds_crossed > 0:
                                        enemy.knock_back()
                                enemy.last_hp = enemy.hp
                                contact_rect = cat_attack_zone.clip(enemy.get_rect())
                                contact_point = contact_rect.center
                                cat.contact_points.append(contact_point)
                                enemy.contact_points.append(contact_point)
                                break
        elif cat.is_aoe:
            targets = [e for e in enemies if cat_attack_zone.colliderect(e.get_rect())]
            if enemy_tower and cat_attack_zone.colliderect(enemy_tower.get_rect()):
                targets.append(enemy_tower)
            if targets and now - cat.last_attack_time > 1000:
                cat.anim_state = "windup"
                cat.anim_start_time = now
                cat.last_attack_time = now
                cat.is_attacking = True
            elif not targets:
                cat.move()
        else:
            if enemy_tower and cat_attack_zone.colliderect(enemy_tower.get_rect()):
                if now - cat.last_attack_time > 1000:
                    cat.anim_state = "windup"
                    cat.anim_start_time = now
                    cat.last_attack_time = now
                    cat.is_attacking = True
            else:
                for enemy in enemies:
                    if cat_attack_zone.colliderect(enemy.get_rect()):
                        if now - cat.last_attack_time > 1000:
                            cat.anim_state = "windup"
                            cat.anim_start_time = now
                            cat.last_attack_time = now
                            cat.is_attacking = True
                        break
                else:
                    cat.move()

    for enemy in enemies:
        enemy_attack_zone = enemy.get_attack_zone()
        if enemy.anim_state in ["windup", "attacking", "recovery"]:
            if enemy.anim_state == "attacking" and now - enemy.last_attack_time >= enemy.frame_durations["attacking"] * len(enemy.anim_frames["attacking"]):
                enemy.last_attack_time = now
                if enemy.is_aoe:
                    targets = [c for c in cats if enemy_attack_zone.colliderect(c.get_rect())]
                    if not enemy.is_boss and enemy_attack_zone.colliderect(our_tower.get_rect()):
                        targets.append(our_tower)
                    for tar in targets:
                        if isinstance(tar, Cat):
                            c = tar
                            old_hp = c.hp
                            c.hp -= enemy.atk
                            if c.hp > 0:
                                thresholds_crossed = int(old_hp / c.kb_threshold) - int(c.hp / c.kb_threshold)
                                if thresholds_crossed > 0:
                                    c.knock_back()
                            c.last_hp = c.hp
                            contact_rect = enemy_attack_zone.clip(c.get_rect())
                            contact_point = contact_rect.center
                            c.contact_points.append(contact_point)
                            enemy.contact_points.append(contact_point)
                        elif isinstance(tar, Tower):
                            tower = tar
                            tower.hp -= enemy.atk
                            contact_rect = enemy_attack_zone.clip(tower.get_rect())
                            contact_point = contact_rect.center
                            tower.contact_points.append(contact_point)
                            enemy.contact_points.append(contact_point)
                else:
                    if not enemy.is_boss and enemy_attack_zone.colliderect(our_tower.get_rect()):
                        tower = our_tower
                        tower.hp -= enemy.atk
                        contact_rect = enemy_attack_zone.clip(tower.get_rect())
                        contact_point = contact_rect.center
                        tower.contact_points.append(contact_point)
                        enemy.contact_points.append(contact_point)
                    else:
                        for cat in cats:
                            if enemy_attack_zone.colliderect(cat.get_rect()):
                                old_hp = cat.hp
                                cat.hp -= enemy.atk
                                if cat.hp > 0:
                                    thresholds_crossed = int(old_hp / cat.kb_threshold) - int(cat.hp / cat.kb_threshold)
                                    if thresholds_crossed > 0:
                                        cat.knock_back()
                                cat.last_hp = cat.hp
                                contact_rect = enemy_attack_zone.clip(cat.get_rect())
                                contact_point = contact_rect.center
                                cat.contact_points.append(contact_point)
                                enemy.contact_points.append(contact_point)
                                break
        elif enemy.is_aoe:
            targets = [c for c in cats if enemy_attack_zone.colliderect(c.get_rect())]
            if not enemy.is_boss and enemy_attack_zone.colliderect(our_tower.get_rect()):
                targets.append(our_tower)
            if targets and now - enemy.last_attack_time > 1000:
                enemy.anim_state = "windup"
                enemy.anim_start_time = now
                enemy.last_attack_time = now
                enemy.is_attacking = True
            elif not targets:
                enemy.move()
        else:
            if not enemy.is_boss and enemy_attack_zone.colliderect(our_tower.get_rect()):
                if now - enemy.last_attack_time > 1000:
                    enemy.anim_state = "windup"
                    enemy.anim_start_time = now
                    enemy.last_attack_time = now
                    enemy.is_attacking = True
            else:
                for cat in cats:
                    if enemy_attack_zone.colliderect(cat.get_rect()):
                        if now - enemy.last_attack_time > 1000:
                            enemy.anim_state = "windup"
                            enemy.anim_start_time = now
                            enemy.last_attack_time = now
                            enemy.is_attacking = True
                        break
                else:
                    enemy.move()

    # Centralized soul creation for enemy deaths
    new_enemies = []
    for enemy in enemies:
        if enemy.hp > 0:
            new_enemies.append(enemy)
        else:
            souls.append(Soul(enemy.x + enemy.width // 2, enemy.y))
            # Optional debug: print(f"Soul created for enemy at ({enemy.x}, {enemy.y})")
    enemies[:] = new_enemies

    # Centralized soul creation for cat deaths
    new_cats = []
    for cat in cats:
        if cat.hp > 0:
            new_cats.append(cat)
        else:
            souls.append(Soul(cat.x + cat.width // 2, cat.y))
            # Optional debug: print(f"Soul created for cat at ({cat.x}, {cat.y})")
    cats[:] = new_cats

    if enemy_tower and enemy_tower.hp <= 0:
        enemy_tower.hp = 0
    if our_tower.hp <= 0:
        our_tower.hp = 0

# === Game Setup ===
pygame.init()
screen = pygame.display.set_mode((1000, 600))
pygame.display.set_caption("Battle Cats: Attack Range")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)
end_font = pygame.font.SysFont(None, 96)
FPS = 60
background_color = (200, 255, 200)

# === Level Selection Screen ===
def draw_level_selection(screen, levels, selected_level, selected_cats):
    screen.fill(background_color)
    title = font.render("Select Level and Cats", True, (0, 0, 0))
    screen.blit(title, (350, 50))
    for i, level in enumerate(levels):
        rect = pygame.Rect(50, 100 + i * 60, 200, 50)
        color = (0, 255, 0) if i == selected_level else (100, 200, 100)
        pygame.draw.rect(screen, color, rect)
        level_text = font.render(level.name, True, (0, 0, 0))
        screen.blit(level_text, (rect.x + 5, rect.y + 15))
    cat_rects = {}
    for idx, cat_type in enumerate(cat_types.keys()):
        rect = pygame.Rect(300 + idx * 150, 100, 100, 50)
        cat_rects[cat_type] = rect
        color = (0, 255, 0) if cat_type in selected_cats else (200, 200, 200)
        pygame.draw.rect(screen, color, rect)
        screen.blit(font.render(cat_type, True, (0, 0, 0)), (rect.x + 5, rect.y + 15))
    screen.blit(font.render("Click to select level, click to toggle cats, press Enter to start", True, (0, 0, 0)), (50, 400))
    return cat_rects

# === Game Loop ===
async def main():
    game_state = "level_selection"
    selected_level = 0
    selected_cats = list(cat_types.keys())[:2]
    cats = []
    enemies = []
    souls = []
    cat_y = 450
    enemy_y = 450
    our_tower = None
    enemy_tower = None
    last_spawn_time = {cat_type: 0 for cat_type in cat_types}
    last_enemy_spawn_time = {i: -levels[0].enemy_types[i].get("initial_delay", 0) for i in range(len(levels[0].enemy_types))}
    last_budget_increase_time = -333
    total_budget_limitation = 16500
    current_budget = 1000
    budget_rate = 33
    status = 0
    level_start_time = 0
    cat_key_map = {pygame.K_1: selected_cats[0]} if len(selected_cats) > 0 else {}
    if len(selected_cats) > 1:
        cat_key_map[pygame.K_2] = selected_cats[1]
    if len(selected_cats) > 2:
        cat_key_map[pygame.K_3] = selected_cats[2]
    button_rects = {}
    for idx, cat_type in enumerate(selected_cats):
        button_rects[cat_type] = pygame.Rect(50 + idx * 150, 50, 100, 50)
    button_colors = {"normal": (100, 200, 100), "cooldown": (180, 180, 180)}
    while True:
        current_time = pygame.time.get_ticks()
        if game_state == "level_selection":
            cat_rects = draw_level_selection(screen, levels, selected_level, selected_cats)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    for i, level in enumerate(levels):
                        if pygame.Rect(50, 100 + i * 60, 200, 50).collidepoint(pos):
                            selected_level = i
                    for cat_type, rect in cat_rects.items():
                        if rect.collidepoint(pos):
                            if cat_type in selected_cats and len(selected_cats) > 1:
                                selected_cats.remove(cat_type)
                            elif len(selected_cats) < 3:
                                selected_cats.append(cat_type)
                            cat_key_map = {pygame.K_1: selected_cats[0]} if len(selected_cats) > 0 else {}
                            if len(selected_cats) > 1:
                                cat_key_map[pygame.K_2] = selected_cats[1]
                            if len(selected_cats) > 2:
                                cat_key_map[pygame.K_3] = selected_cats[2]
                            button_rects = {cat_type: pygame.Rect(50 + idx * 150, 50, 100, 50) for idx, cat_type in enumerate(selected_cats)}
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    game_state = "playing"
                    current_level = levels[selected_level]
                    current_level.reset_towers()
                    our_tower = current_level.our_tower
                    enemy_tower = current_level.enemy_tower
                    for et in current_level.enemy_types:
                        key = (et["type"], et.get("variant", "default"))
                        current_level.spawned_counts[key] = 0
                    current_level.all_limited_spawned = False
                    cats = []
                    souls = []
                    enemies = []
                    current_budget = 1000
                    last_enemy_spawn_time = {(et["type"], et.get("variant", "default")): -et.get("initial_delay", 0) for et in current_level.enemy_types}
                    last_budget_increase_time = -333
                    last_spawn_time = {cat_type: 0 for cat_type in cat_types}
                    status = 0
                    level_start_time = current_time
            pygame.display.flip()
        elif game_state == "playing":
            current_level = levels[selected_level]
            screen.blit(current_level.background, (0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key in cat_key_map and current_budget >= cat_costs[cat_key_map[event.key]]:
                        current_budget -= cat_costs[cat_key_map[event.key]]
                        cat_type = cat_key_map[event.key]
                        if current_time - last_spawn_time[cat_type] >= cat_cooldowns[cat_type]:
                            start_x = 1000 - 100
                            cats.append(cat_types[cat_type](start_x, cat_y))
                            last_spawn_time[cat_type] = current_time
            if current_time - last_budget_increase_time >= 333:
                if current_budget < total_budget_limitation:
                    current_budget = min(current_budget + budget_rate, total_budget_limitation)
                    last_budget_increase_time = current_time
            tower_hp_percent = (enemy_tower.hp / enemy_tower.max_hp) * 100 if enemy_tower else 0
            for et in current_level.enemy_types:
                key = (et["type"], et.get("variant", ""))
                if (not et["is_limited"] or current_level.spawned_counts[key] < et["spawn_count"]) and tower_hp_percent <= et["tower_hp_percent"]:
                    interval = et["spawn_interval_1"]
                    if current_time - current_level.last_spawn_times[key] >= interval:
                        enemies.append(enemy_types[et["type"]](20, enemy_y, is_b=et["is_boss"]))
                        current_level.spawned_counts[key] += 1
                        current_level.last_spawn_times[key] = current_time
            current_level.all_limited_spawned = current_level.check_all_limited_spawned()
            update_battle(cats, enemies, our_tower, enemy_tower, current_time, souls)
            souls[:] = [soul for soul in souls if soul.update()]
            for soul in souls:
                soul.draw(screen)
            budget_text = font.render(f"Money: {current_budget}", True, (0, 0, 0))
            screen.blit(budget_text, (800, 10))
            if enemy_tower:
                tower_hp_percent = (enemy_tower.hp / enemy_tower.max_hp) * 100
                hp_text = font.render(f"Enemy Tower HP: {tower_hp_percent:.2f}%", True, (0, 0, 0))
                screen.blit(hp_text, (800, 50))
            if current_level.survival_time > 0:
                elapsed_time = (current_time - level_start_time) / 1000
                time_text = font.render(f"Time: {elapsed_time:.1f}s", True, (0, 0, 0))
                screen.blit(time_text, (800, 30))
            for cat in cats:
                cat.draw(screen)
            for enemy in enemies:
                enemy.draw(screen)
            our_tower.draw(screen)
            if enemy_tower:
                enemy_tower.draw(screen)
            for cat_id, rect in button_rects.items():
                time_since = current_time - last_spawn_time[cat_id]
                cooldown = cat_cooldowns[cat_id]
                is_ready = time_since >= cooldown
                color = button_colors["normal"] if is_ready else button_colors["cooldown"]
                pygame.draw.rect(screen, color, rect)
                name_label = font.render(f"{cat_id} ({pygame.key.name(list(cat_key_map.keys())[list(cat_key_map.values()).index(cat_id)])})", True, (0, 0, 0))
                cost_label = font.render(f"Cost: ${cat_costs[cat_id]}", True, (255, 50, 50))
                screen.blit(name_label, (rect.x + 10, rect.y + 5))
                screen.blit(cost_label, (rect.x + 10, rect.y + 25))
                if not is_ready:
                    ratio = time_since / cooldown
                    bar_width = rect.width * ratio
                    pygame.draw.rect(screen, (50, 255, 50), (rect.x, rect.y + rect.height - 5, bar_width, 5))
            screen.blit(font.render(f"Level: {current_level.name}", True, (0, 0, 0)), (10, 10))
            pygame.display.flip()
            if our_tower.hp <= 0:
                status = "lose"
                game_state = "end"
            elif enemy_tower:
                if enemy_tower.hp <= 0:
                    status = "victory"
                    game_state = "end"
                elif current_level.all_limited_spawned and not any(
                    et["is_limited"] is False for et in current_level.enemy_types
                ) and not enemies:
                    status = "victory"
                    game_state = "end"
                elif current_level.survival_time > 0 and (current_time - level_start_time) >= current_level.survival_time * 1000:
                    status = "victory"
                    game_state = "end"
        elif game_state == "end":
            current_level = levels[selected_level]
            screen.blit(current_level.background, (0, 0))
            if status == "victory":
                text = end_font.render("Victory!", True, (0, 255, 100))
            else:
                text = end_font.render("Defeat!", True, (255, 100, 100))
            screen.blit(text, (350, 250))
            screen.blit(font.render("Press any key to return to level selection", True, (0, 0, 0)), (350, 350))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    game_state = "level_selection"
                    our_tower = None
                    enemy_tower = None
        await asyncio.sleep(1 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())