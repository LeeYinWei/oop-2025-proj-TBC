import asyncio
import platform
import pygame
import random
import sys

# === Classes ===
class Cat:
    def __init__(self, x, y, hp, atk, speed, color, attack_range=50, is_aoe=False):
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

    def move(self):
        if not self.is_attacking:
            self.x -= self.speed

    def draw(self, screen):
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
    def __init__(self, x, y, hp, atk, speed, color, attack_range=50, is_aoe=False):
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

    def move(self):
        if not self.is_attacking:
            self.x += self.speed

    def draw(self, screen):
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
        return pygame.Rect(self.x + self.width, self.y, self.attack_range, self.height)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Tower:
    def __init__(self, x, y, hp, color):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = hp
        self.color = color
        self.last_attack_time = 0
        self.width = 120
        self.height = 400
        self.is_attacking = False
        self.contact_points = []

    def draw(self, screen):
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
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Level:
    def __init__(self, name, enemy_types, spawn_interval, total_enemies, enemy_tower_hp):
        self.name = name
        self.enemy_types = enemy_types
        self.spawn_interval = spawn_interval
        self.total_enemies = total_enemies
        self.enemy_tower_hp = enemy_tower_hp
        self.enemies_spawned = 0

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
    enemy_tower.contact_points = []
    # Cats attack enemies
    for cat in cats:
        cat_attack_zone = cat.get_attack_zone()
        if cat.is_aoe:
            targets = [e for e in enemies if cat_attack_zone.colliderect(e.get_rect())]
            if cat_attack_zone.colliderect(enemy_tower.get_rect()):
                targets.append(enemy_tower)
            if targets and now - cat.last_attack_time > 1000:
                for tar in targets:
                    if isinstance(tar, Enemy):
                        e = tar
                        e.hp -= cat.atk
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
            if cat_attack_zone.colliderect(enemy_tower.get_rect()):
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
                            enemy.hp -= cat.atk
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
            if enemy_attack_zone.colliderect(our_tower.get_rect()):
                targets.append(our_tower)
            if targets and now - enemy.last_attack_time > 1000:
                for tar in targets:
                    if isinstance(tar, Cat):
                        cat = tar
                        cat.hp -= enemy.atk
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
            if enemy_attack_zone.colliderect(our_tower.get_rect()):
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
                            cat.hp -= enemy.atk
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
pygame.display.set_caption("貓咪大戰爭：攻擊範圍內")
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
    print(f"無法載入背景圖片 'background/background1.png': {e}")
    pygame.quit()
    sys.exit()

# === Data ===
cat_types = {
    "basic": lambda x, y: Cat(x, y, hp=100, atk=10, speed=1, color=(200, 200, 200), attack_range=50, is_aoe=False),
    "speedy": lambda x, y: Cat(x, y, hp=70, atk=5, speed=2, color=(150, 150, 150), attack_range=30, is_aoe=False),
    "tank": lambda x, y: Cat(x, y, hp=150, atk=15, speed=0.5, color=(120, 120, 120), attack_range=60, is_aoe=True),
}

cat_cooldowns = {
    "basic": 1000,
    "speedy": 500,
    "tank": 2000,
}

cat_costs = {
    "basic": 100,
    "speedy": 150,
    "tank": 300,
}

enemy_types = {
    "basic": lambda x, y: Enemy(x, y, hp=100, atk=10, speed=1, color=(255, 100, 100), attack_range=40, is_aoe=False),
    "fast": lambda x, y: Enemy(x, y, hp=50, atk=5, speed=2, color=(255, 150, 150), attack_range=30, is_aoe=False),
    "tank": lambda x, y: Enemy(x, y, hp=200, atk=15, speed=0.5, color=(100, 50, 50), attack_range=60, is_aoe=True),
}

levels = [
    Level("Level 1: Easy", [("basic", 0.8), ("fast", 0.2)], 3000, 10, 1000),
    Level("Level 2: Medium", [("basic", 0.5), ("fast", 0.3), ("tank", 0.2)], 2000, 15, 1500),
    Level("Level 3: Hard", [("fast", 0.4), ("tank", 0.6)], 1500, 20, 2000),
]

# === Level Selection Screen ===
def draw_level_selection(screen, levels, selected_level, selected_cats):
    screen.fill(background_color)
    title = font.render("選擇關卡與貓咪", True, (0, 0, 0))
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
    
    screen.blit(font.render("點擊選擇關卡，點擊切換貓咪，按 Enter 開始", True, (0, 0, 0)), (50, 400))
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
                    enemy_tower = Tower(20, 140, hp=levels[selected_level].enemy_tower_hp, color=(150, 50, 150))
                    levels[selected_level].enemies_spawned = 0
                    cats = []
                    enemies = []
                    current_budget = 1000
                    last_enemy_spawn_time = -levels[selected_level].spawn_interval
                    last_budget_increase_time = -333
                    last_spawn_time = {cat_type: 0 for cat_type in cat_types}
                    status = 0
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
            if current_time - last_enemy_spawn_time >= current_level.spawn_interval and current_level.enemies_spawned < current_level.total_enemies:
                enemy_choice = random.choices(
                    [et[0] for et in current_level.enemy_types],
                    weights=[et[1] for et in current_level.enemy_types],
                    k=1
                )[0]
                enemies.append(enemy_types[enemy_choice](20, enemy_y))
                last_enemy_spawn_time = current_time
                current_level.enemies_spawned += 1
            
            # Increase budget every 1/3 second
            if current_time - last_budget_increase_time >= 333:  # 333ms ≈ 1/3 second
                if current_budget < total_budget_limitation:
                    current_budget = min(current_budget + budget_rate, total_budget_limitation)
                    last_budget_increase_time = current_time
            
            # Update battle
            update_battle(cats, enemies, our_tower, enemy_tower, current_time)
            
            # Draw budget
            budget_text = font.render(f"當前金錢: {current_budget}", True, (0, 0, 0))
            screen.blit(budget_text, (800, 10))
            
            # Draw units
            for cat in cats:
                cat.draw(screen)
            for enemy in enemies:
                enemy.draw(screen)
            
            # Draw towers
            our_tower.draw(screen)
            enemy_tower.draw(screen)
            
            # Draw cooldown buttons
            for cat_type, rect in button_rects.items():
                time_since = current_time - last_spawn_time[cat_type]
                cooldown = cat_cooldowns[cat_type]
                is_ready = time_since >= cooldown
                color = button_colors["normal"] if is_ready else button_colors["cooldown"]
                pygame.draw.rect(screen, color, rect)
                name_label_text = f"{cat_type} ({list(cat_key_map.keys())[list(cat_key_map.values()).index(cat_type)] - 48})"
                cost_label_text = f"花費: {cat_costs[cat_type]}"
                name_label = font.render(name_label_text, True, (0, 0, 0))
                cost_label = font.render(cost_label_text, True, (255, 0, 0))
                screen.blit(name_label, (rect.x + 5, rect.y + 5))
                screen.blit(cost_label, (rect.x + 5, rect.y + 23))
                if not is_ready:
                    ratio = time_since / cooldown
                    bar_width = rect.width * (1 - ratio)
                    pygame.draw.rect(screen, (255, 100, 100), (rect.x, rect.y + rect.height - 5, bar_width, 5))
            
            # Draw instruction text
            screen.blit(font.render(f"關卡: {current_level.name}", True, (0, 0, 0)), (10, 10))
            screen.blit(font.render("按 1, 2, 3 生成選擇的貓貓", True, (0, 0, 0)), (10, 30))
            screen.blit(font.render("紅點表示攻擊接觸點", True, (255, 0, 0)), (10, 50))
            
            pygame.display.flip()
            
            # Check win/lose conditions
            if our_tower.hp <= 0:
                status = 2  # lose
                game_state = "end"
            elif enemy_tower.hp <= 0 or (current_level.enemies_spawned >= current_level.total_enemies and not enemies):
                status = 1  # win
                game_state = "end"
        
        elif game_state == "end":
            screen.blit(background_img, (0, 0))
            if status == 1:
                screen.blit(end_font.render("你贏了！", True, (0, 255, 0)), (350, 200))
            elif status == 2:
                screen.blit(end_font.render("你輸了！", True, (255, 0, 0)), (350, 200))
            screen.blit(font.render("按任意鍵返回關卡選擇", True, (0, 0, 0)), (360, 270))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    game_state = "level_selection"
                    our_tower = Tower(850, 140, hp=1000, color=(100, 100, 255))
        
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())