import asyncio
import platform
import pygame
import random
import sys
import os
import importlib.util

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
        cfg["attack_range"], cfg["is_aoe"], cfg["image_path"], cfg["kb_limit"]
    )
    cat_cooldowns[cat_type] = config["cooldown"]
    cat_costs[cat_type] = config["cost"]


# === Classes ===
class Cat:
    def __init__(self, x, y, hp, atk, speed, color, attack_range=50, is_aoe=False, image_path=None, kb_limit=1):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = hp
        self.atk = atk
        self.speed = speed
        self.color = color
        self.attack_range = attack_range
        self.is_aoe = is_aoe
        self.last_attack_time = 0
        self.width = 40
        self.height = 40
        self.is_attacking = False
        self.contact_points = []
        self.kb_limit = kb_limit
        self.kb_count = 0
        self.kb_threshold = self.max_hp / self.kb_limit if self.kb_limit > 0 else self.max_hp
        self.last_hp = hp  # Track HP for KB detection
        self.image = None
        if image_path:
            try:
                self.image = pygame.image.load(image_path)
                self.image = pygame.transform.scale(self.image, (self.width, self.height))
            except pygame.error as e:
                print(f"Cannot load cat image '{image_path}': {e}")
                self.image = None

    def move(self):
        if not self.is_attacking:
            self.x -= self.speed

    def knock_back(self):
        self.x += 50  # Cat moves right (backwards)
        self.kb_count += 1
        if self.kb_count >= self.kb_limit:
            self.hp = 0  # Die if KB limit reached

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.x, self.y))
        else:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        self.draw_hp_bar(screen)
        for pt in self.contact_points:
            pygame.draw.circle(screen, (255, 0, 0), pt, 5)

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

class Enemy:
    def __init__(self, x, y, hp, speed, color, attack_range=50, is_aoe=False, image_path=None, is_boss=False, is_b=False, atk=10, kb_limit=1):
        self.x = x
        self.y = y
        self.hp = hp * (2 if is_b else 1)  # Boss has double HP
        self.max_hp = self.hp
        self.atk = atk * (1.5 if is_b else 1)  # Boss has 1.5x attack
        self.speed = speed
        self.color = color
        self.attack_range = attack_range
        self.is_aoe = is_aoe
        self.is_boss = is_b
        self.last_attack_time = 0
        self.width = 40
        self.height = 40
        self.is_attacking = False
        self.contact_points = []
        self.kb_limit = kb_limit
        self.kb_count = 0
        self.kb_threshold = self.max_hp / self.kb_limit if self.kb_limit > 0 else self.max_hp
        self.last_hp = hp  # Track HP for KB detection
        self.image = None
        if image_path:
            try:
                self.image = pygame.image.load(image_path)
                self.image = pygame.transform.scale(self.image, (self.width, self.height))
            except pygame.error as e:
                print(f"Cannot load enemy image '{image_path}': {e}")
                self.image = None

    def move(self):
        if not self.is_attacking:
            self.x += self.speed

    def knock_back(self):
        self.x -= 50  # Enemy moves left (backwards)
        self.kb_count += 1
        if self.kb_count >= self.kb_limit:
            self.hp = 0  # Die if KB limit reached

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.x, self.y))
        else:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        self.draw_hp_bar(screen)
        if self.is_boss:
            boss_label = pygame.font.SysFont(None, 20).render("Boss", True, (255, 0, 0))
            screen.blit(boss_label, (self.x, self.y - 20))
        for pt in self.contact_points:
            pygame.draw.circle(screen, (255, 0, 0), pt, 5)

    def draw_hp_bar(self, screen):
        bar_width = self.width
        bar_height = 5
        fill = max(0, self.hp / self.max_hp) * bar_width
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y - 10, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 10, fill, bar_height))

    def get_attack_zone(self):
        return pygame.Rect(self.x + self.width, self.y, self.attack_range, self.height)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Tower:
    def __init__(self, x, y, hp, color, tower_path="tower/tower1.png", is_enemy=False):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = hp
        self.color = color
        self.last_attack_time = 0
        self.is_attacking = False
        self.contact_points = []
        self.is_enemy = is_enemy
        if is_enemy:
            try:
                self.image = pygame.image.load(tower_path)
                orig_width, orig_height = self.image.get_size()
                aspect_ratio = orig_width / orig_height
                self.height = 100
                self.width = int(self.height * aspect_ratio)
                self.image = pygame.transform.scale(self.image, (self.width, self.height))
            except pygame.error as e:
                print(f"Cannot load tower image '{tower_path}': {e}")
                pygame.quit()
                sys.exit()
        else:
            self.width = 120
            self.height = 400

    def draw(self, screen):
        if self.is_enemy:
            screen.blit(self.image, (self.x, self.y))
        else:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        self.draw_hp_bar(screen)
        for pt in self.contact_points:
            pygame.draw.circle(screen, (255, 0, 0), pt, 5)

    def draw_hp_bar(self, screen):
        bar_width = self.width
        bar_height = 5
        fill = max(0, self.hp / self.max_hp) * bar_width
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y - 10, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 10, fill, bar_height))

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, int(self.height))

class Level:
    def __init__(self, name, enemy_types, spawn_interval, enemy_tower_hp, survival_time):
        self.name = name
        self.enemy_types = enemy_types
        self.spawn_interval = spawn_interval
        self.enemy_tower_hp = enemy_tower_hp
        self.survival_time = survival_time
        self.spawned_counts = {et["type"]: 0 for et in enemy_types}
        self.all_limited_spawned = False

    def check_all_limited_spawned(self):
        for et in self.enemy_types:
            if et["is_limited"] and self.spawned_counts[et["type"]] < et["spawn_count"]:
                return False
        return True
# Load levels from level_folder
levels = []
level_folders = ["level_1", "level_2", "level_3"]
for level_folder in level_folders:
    config = load_config("level_folder", level_folder)
    levels.append(Level(
        config["name"],
        config["enemy_types"],
        config["spawn_interval"],
        config["enemy_tower_hp"],
        config["survival_time"]
    ))
enemy_types = {}
for enemy_type in ["basic", "fast", "tank"]:
    config = load_config("enemy_folder", enemy_type)
    enemy_types[enemy_type] = lambda x, y, is_b, cfg=config: Enemy(
        x, y, cfg["hp"], cfg["speed"], cfg["color"], cfg["attack_range"],
        cfg["is_aoe"], cfg["image_path"], is_boss=cfg.get("is_boss", False),
        atk=cfg["atk"], kb_limit=cfg["kb_limit"]
    )


# === Battle Logic ===
def update_battle(cats, enemies, our_tower, enemy_tower, now):
    # Clear contact points
    for cat in cats:
        cat.is_attacking = False
        cat.contact_points = []
    for enemy in enemies:
        enemy.is_attacking = False
        enemy.contact_points = []
    our_tower.contact_points = []
    if enemy_tower:
        enemy_tower.contact_points = []

    # Cats attack enemies
    for cat in cats:
        cat_attack_zone = cat.get_attack_zone()
        if cat.is_aoe:
            targets = [e for e in enemies if cat_attack_zone.colliderect(e.get_rect())]
            if enemy_tower and cat_attack_zone.colliderect(enemy_tower.get_rect()):
                targets.append(enemy_tower)
            if targets and now - cat.last_attack_time > 1000:
                for tar in targets:
                    if isinstance(tar, Enemy):
                        e = tar
                        old_hp = e.hp
                        e.hp -= cat.atk
                        # Check for knock back
                        if e.hp > 0:
                            thresholds_crossed = int(e.last_hp / e.kb_threshold) - int(e.hp / e.kb_threshold)
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
                cat.last_attack_time = now
                cat.is_attacking = True
            elif not targets:
                cat.is_attacking = False
                cat.move()
        else:
            if enemy_tower and cat_attack_zone.colliderect(enemy_tower.get_rect()):
                tower = enemy_tower
                if now - cat.last_attack_time > 1000:
                    tower.hp -= cat.atk
                    cat.last_attack_time = now
                    cat.is_attacking = True
                    contact_rect = cat_attack_zone.clip(tower.get_rect())
                    contact_point = contact_rect.center
                    tower.contact_points.append(contact_point)
                    cat.contact_points.append(contact_point)
            else:
                for enemy in enemies:
                    if cat_attack_zone.colliderect(enemy.get_rect()):
                        if now - cat.last_attack_time > 1000:
                            old_hp = enemy.hp
                            enemy.hp -= cat.atk
                            # Check for knock back
                            if enemy.hp > 0:
                                thresholds_crossed = int(old_hp / enemy.kb_threshold) - int(enemy.hp / enemy.kb_threshold)
                                if thresholds_crossed > 0:
                                    enemy.knock_back()
                            enemy.last_hp = enemy.hp
                            cat.last_attack_time = now
                            cat.is_attacking = True
                            contact_rect = cat_attack_zone.clip(enemy.get_rect())
                            contact_point = contact_rect.center
                            cat.contact_points.append(contact_point)
                            enemy.contact_points.append(contact_point)
                        break
                else:
                    cat.is_attacking = False
                    cat.move()

    # Enemies attack cats
    for enemy in enemies:
        enemy_attack_zone = enemy.get_attack_zone()
        if enemy.is_aoe:
            targets = [c for c in cats if enemy_attack_zone.colliderect(c.get_rect())]
            if not enemy.is_boss and enemy_attack_zone.colliderect(our_tower.get_rect()):
                targets.append(our_tower)
            if targets and now - enemy.last_attack_time > 1000:
                for tar in targets:
                    if isinstance(tar, Cat):
                        cat = tar
                        old_hp = cat.hp
                        cat.hp -= enemy.atk
                        # Check for knock back
                        if cat.hp > 0:
                            thresholds_crossed = int(old_hp / cat.kb_threshold) - int(cat.hp / cat.kb_threshold)
                            if thresholds_crossed > 0:
                                cat.knock_back()
                        cat.last_hp = cat.hp
                        contact_rect = enemy_attack_zone.clip(cat.get_rect())
                        contact_point = contact_rect.center
                        cat.contact_points.append(contact_point)
                        enemy.contact_points.append(contact_point)
                    elif isinstance(tar, Tower):
                        tower = tar
                        tower.hp -= enemy.atk
                        contact_rect = enemy_attack_zone.clip(tower.get_rect())
                        contact_point = contact_rect.center
                        tower.contact_points.append(contact_point)
                        enemy.contact_points.append(contact_point)
                enemy.last_attack_time = now
                enemy.is_attacking = True
            elif not targets:
                enemy.is_attacking = False
                enemy.move()
        else:
            if not enemy.is_boss and enemy_attack_zone.colliderect(our_tower.get_rect()):
                tower = our_tower
                if now - enemy.last_attack_time > 1000:
                    tower.hp -= enemy.atk
                    enemy.last_attack_time = now
                    enemy.is_attacking = True
                    contact_rect = enemy_attack_zone.clip(tower.get_rect())
                    contact_point = contact_rect.center
                    tower.contact_points.append(contact_point)
                    enemy.contact_points.append(contact_point)
            else:
                for cat in cats:
                    if enemy_attack_zone.colliderect(cat.get_rect()):
                        if now - enemy.last_attack_time > 1000:
                            old_hp = cat.hp
                            cat.hp -= enemy.atk
                            # Check for knock back
                            if cat.hp > 0:
                                thresholds_crossed = int(old_hp / cat.kb_threshold) - int(cat.hp / cat.kb_threshold)
                                if thresholds_crossed > 0:
                                    cat.knock_back()
                            cat.last_hp = cat.hp
                            enemy.last_attack_time = now
                            enemy.is_attacking = True
                            contact_rect = enemy_attack_zone.clip(cat.get_rect())
                            contact_point = contact_rect.center
                            cat.contact_points.append(contact_point)
                            enemy.contact_points.append(contact_point)
                        break
                else:
                    enemy.is_attacking = False
                    enemy.move()

    cats[:] = [c for c in cats if c.hp > 0]
    enemies[:] = [e for e in enemies if e.hp > 0]

# === Game Setup ===
pygame.init()
screen = pygame.display.set_mode((1000, 600))
pygame.display.set_caption("Battle Cats: Attack Range")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)
end_font = pygame.font.SysFont(None, 96)
FPS = 60

# Background setup
background_color = (200, 255, 200)  # Light green for menu
try:
    background_img = pygame.image.load("background/background1.png")
    background_img = pygame.transform.scale(background_img, (1000, 600))
except pygame.error as e:
    print(f"Cannot load background image 'background/background1.png': {e}")
    pygame.quit()
    sys.exit()

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
    
    # Cat selection
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
    global our_tower, enemy_tower
    game_state = "level_selection"
    selected_level = 0
    selected_cats = list(cat_types.keys())[:2]  # Default to first two cats
    cats = []
    enemies = []
    cat_y = 450
    enemy_y = 450
    our_tower = Tower(850, 140, hp=1000, color=(100, 100, 255))
    enemy_tower = None
    last_spawn_time = {cat_type: 0 for cat_type in cat_types}
    last_enemy_spawn_time = -3000
    last_budget_increase_time = -333  # Initialize to allow immediate update
    total_budget_limitation = 16500
    current_budget = 1000
    budget_rate = 33  # Adjusted to 33 for 1/3 second updates (33 * 3 ≈ 99 per second)
    status = 0  # 0 = ongoing, 1 = win, 2 = lose
    level_start_time = 0  # Track level start time for survival
    
    cat_key_map = {pygame.K_1: selected_cats[0]} if len(selected_cats) > 0 else {}
    if len(selected_cats) > 1:
        cat_key_map[pygame.K_2] = selected_cats[1]
    if len(selected_cats) > 2:
        cat_key_map[pygame.K_3] = selected_cats[2]
    
    button_rects = {}
    for idx, cat_type in enumerate(selected_cats):
        button_rects[cat_type] = pygame.Rect(50 + idx * 150, 50, 100, 50)
    
    button_colors = {
        "normal": (100, 200, 100),
        "cooldown": (180, 180, 180),
    }
    
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
                            if cat_type in selected_cats:
                                if len(selected_cats) > 1:  # Ensure at least one cat
                                    selected_cats.remove(cat_type)
                            else:
                                if len(selected_cats) < 3:  # Max 3 cats
                                    selected_cats.append(cat_type)
                            cat_key_map = {pygame.K_1: selected_cats[0]} if len(selected_cats) > 0 else {}
                            if len(selected_cats) > 1:
                                cat_key_map[pygame.K_2] = selected_cats[1]
                            if len(selected_cats) > 2:
                                cat_key_map[pygame.K_3] = selected_cats[2]
                            button_rects = {cat_type: pygame.Rect(50 + idx * 150, 50, 100, 50) for idx, cat_type in enumerate(selected_cats)}
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    game_state = "playing"
                    enemy_tower = Tower(20, 380, hp=levels[selected_level].enemy_tower_hp, color=(150, 50, 150), is_enemy=True)
                    for et in levels[selected_level].enemy_types:
                        levels[selected_level].spawned_counts[et["type"]] = 0
                    levels[selected_level].all_limited_spawned = False
                    cats = []
                    enemies = []
                    current_budget = 1000
                    last_enemy_spawn_time = -levels[selected_level].spawn_interval
                    last_budget_increase_time = -333
                    last_spawn_time = {cat_type: 0 for cat_type in cat_types}
                    status = 0
                    level_start_time = current_time
            pygame.display.flip()
        
        elif game_state == "playing":
            screen.blit(background_img, (0, 0))
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
            
            # Spawn enemies
            current_level = levels[selected_level]
            if current_time - last_enemy_spawn_time >= current_level.spawn_interval:
                tower_hp_percent = (enemy_tower.hp / enemy_tower.max_hp) * 100 if enemy_tower else 0
                eligible_enemies = [
                    et for et in current_level.enemy_types
                    if (not et["is_limited"] or current_level.spawned_counts[et["type"]] < et["spawn_count"])
                    and tower_hp_percent <= et["tower_hp_percent"]
                ]
                if eligible_enemies:
                    weights = [et["weight"] for et in eligible_enemies]
                    enemy_choice = random.choices(eligible_enemies, weights=weights, k=1)[0]
                    enemy_type = enemy_choice["type"]
                    enemies.append(enemy_types[enemy_type](20, enemy_y, is_b=enemy_choice["is_boss"]))
                    current_level.spawned_counts[enemy_type] += 1
                    last_enemy_spawn_time = current_time
                current_level.all_limited_spawned = current_level.check_all_limited_spawned()
            
            # Increase budget every 1/3 second
            if current_time - last_budget_increase_time >= 333:
                if current_budget < total_budget_limitation:
                    current_budget = min(current_budget + budget_rate, total_budget_limitation)
                    last_budget_increase_time = current_time
            
            # Update battle
            update_battle(cats, enemies, our_tower, enemy_tower, current_time)
            
            # Draw budget
            budget_text = font.render(f"Money: {current_budget}", True, (0, 0, 0))
            screen.blit(budget_text, (800, 10))
            
            # Draw tower HP percentage
            if enemy_tower:
                tower_hp_percent = (enemy_tower.hp / enemy_tower.max_hp) * 100
                hp_text = font.render(f"Enemy Tower HP: {tower_hp_percent:.1f}%", True, (0, 0, 0))
                screen.blit(hp_text, (800, 50))
            
            # Draw survival time if survival_time is set
            if current_level.survival_time > 0:
                elapsed_time = (current_time - level_start_time) // 1000  # Seconds
                time_text = font.render(f"Time: {elapsed_time}s", True, (0, 0, 0))
                screen.blit(time_text, (800, 30))
            
            # Draw units
            for cat in cats:
                cat.draw(screen)
            for enemy in enemies:
                enemy.draw(screen)
            
            # Draw towers
            our_tower.draw(screen)
            if enemy_tower:
                enemy_tower.draw(screen)
            
            # Draw cooldown buttons
            for cat_type, rect in button_rects.items():
                time_since = current_time - last_spawn_time[cat_type]
                cooldown = cat_cooldowns[cat_type]
                is_ready = time_since >= cooldown
                color = button_colors["normal"] if is_ready else button_colors["cooldown"]
                pygame.draw.rect(screen, color, rect)
                name_label_text = f"{cat_type} ({list(cat_key_map.keys())[list(cat_key_map.values()).index(cat_type)] - 48})"
                cost_label_text = f"Cost: {cat_costs[cat_type]}"
                name_label = font.render(name_label_text, True, (0, 0, 0))
                cost_label = font.render(cost_label_text, True, (255, 0, 0))
                screen.blit(name_label, (rect.x + 5, rect.y + 5))
                screen.blit(cost_label, (rect.x + 5, rect.y + 23))
                if not is_ready:
                    ratio = time_since / cooldown
                    bar_width = rect.width * (1 - ratio)
                    pygame.draw.rect(screen, (255, 100, 100), (rect.x, rect.y + rect.height - 5, bar_width, 5))
            
            # Draw instruction text
            screen.blit(font.render(f"Level: {current_level.name}", True, (0, 0, 0)), (10, 10))
            screen.blit(font.render("Press 1, 2, 3 to spawn cats", True, (0, 0, 0)), (10, 30))
            screen.blit(font.render("Red dots indicate attack contact points", True, (255, 0, 0)), (10, 50))
            
            pygame.display.flip()
            
            # Check win/lose conditions
            if our_tower.hp <= 0:
                status = 2  # lose
                game_state = "end"
            elif enemy_tower:
                if enemy_tower.hp <= 0:
                    status = 1  # win
                    game_state = "end"
                elif current_level.all_limited_spawned and not any(
                    et["is_limited"] is False for et in current_level.enemy_types
                ) and not enemies:
                    status = 1  # win (all limited enemies cleared, no unlimited enemies)
                    game_state = "end"
                elif current_level.survival_time > 0 and (current_time - level_start_time) >= current_level.survival_time:
                    status = 1  # win (survived long enough)
                    game_state = "end"
        
        elif game_state == "end":
            screen.blit(background_img, (0, 0))
            if status == 1:
                screen.blit(end_font.render("You Win!", True, (0, 255, 0)), (350, 200))
            elif status == 2:
                screen.blit(end_font.render("You Lose!", True, (255, 0, 0)), (350, 200))
            screen.blit(font.render("Press any key to return to level selection", True, (0, 0, 0)), (360, 270))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    game_state = "level_selection"
                    our_tower = Tower(850, 140, hp=1000, color=(100, 100, 255))
                    enemy_tower = None
        
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())