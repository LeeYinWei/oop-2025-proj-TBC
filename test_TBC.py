import pygame
import random

class Cat:
    def __init__(self, x, y, hp, atk, speed, cat_img=None, attack_range=50, is_aoe=False):
        self.x = x
        self.y = y
        self.hp = hp
        self.atk = atk
        self.speed = speed
        self.attack_range = attack_range
        self.is_aoe = is_aoe
        self.last_attack_time = 0
        self.cat_img = pygame.image.load(cat_img) if cat_img else None
        self.width = self.cat_img.get_width() if self.cat_img else 40
        self.height = self.cat_img.get_height() if self.cat_img else 40
        self.is_attacking = False
        self.contact_points = []

    def move(self):
        if not self.is_attacking:
            self.x -= self.speed

    def draw(self, screen):
        if self.cat_img:
            screen.blit(self.cat_img, (self.x, self.y))
        else:
            pygame.draw.rect(screen, (200, 200, 200), (self.x, self.y, self.width, self.height))

        # 畫血條
        self.draw_hp_bar(screen)

        # 畫接觸點 (紅色小圓)
        for pt in self.contact_points:
            pygame.draw.circle(screen, (255, 0, 0), pt, 5)

    def draw_hp_bar(self, screen):
        bar_width = self.width
        bar_height = 5
        fill = max(0, self.hp / 100) * bar_width
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y - 10, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 10, fill, bar_height))

    def get_attack_zone(self):
        # 從右往左，所以攻擊範圍在左方
        return pygame.Rect(self.x - self.attack_range, self.y, self.attack_range, self.height)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Enemy:
    def __init__(self, x, y, hp, atk, speed, enemy_img=None, attack_range=50, is_aoe=False):
        self.x = x
        self.y = y
        self.hp = hp
        self.atk = atk
        self.speed = speed
        self.attack_range = attack_range
        self.is_aoe = is_aoe
        self.last_attack_time = 0
        self.enemy_img = pygame.image.load(enemy_img) if enemy_img else None
        self.width = self.enemy_img.get_width() if self.enemy_img else 40
        self.height = self.enemy_img.get_height() if self.enemy_img else 40
        self.is_attacking = False
        self.contact_points = []

    def move(self):
        if not self.is_attacking:
            self.x += self.speed

    def draw(self, screen):
        if self.enemy_img:
            screen.blit(self.enemy_img, (self.x, self.y))
        else:
            pygame.draw.rect(screen, (255, 100, 100), (self.x, self.y, self.width, self.height))

        # 畫血條
        self.draw_hp_bar(screen)

        # 畫接觸點 (紅色小圓)
        for pt in self.contact_points:
            pygame.draw.circle(screen, (255, 0, 0), pt, 5)

    def draw_hp_bar(self, screen):
        bar_width = self.width
        bar_height = 5
        fill = max(0, self.hp / 100) * bar_width
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y - 10, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 10, fill, bar_height))

    def get_attack_zone(self):
        # 從左往右，攻擊範圍在右方
        return pygame.Rect(self.x + self.width, self.y, self.attack_range, self.height)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

def update_battle(cats, enemies, now):
    # 先清空接觸點
    for cat in cats:
        cat.is_attacking = False
        cat.contact_points = []
    for enemy in enemies:
        enemy.is_attacking = False
        enemy.contact_points = []

    # 我方攻擊敵人
    for cat in cats:
        cat_attack_zone = cat.get_attack_zone()

        if cat.is_aoe:
            targets = [e for e in enemies if cat_attack_zone.colliderect(e.get_rect())]
            if targets and now - cat.last_attack_time > 1000:
                for enemy in targets:
                    enemy.hp -= cat.atk
                    enemy.is_attacking = True
                    # 記錄接觸點 (兩矩形交集中心)
                    contact_rect = cat_attack_zone.clip(enemy.get_rect())
                    contact_point = contact_rect.center
                    enemy.contact_points.append(contact_point)
                    cat.contact_points.append(contact_point)
                cat.last_attack_time = now
                cat.is_attacking = True
            else:
                cat.move()
        else:
            for enemy in enemies:
                if cat_attack_zone.colliderect(enemy.get_rect()):
                    if now - cat.last_attack_time > 1000:
                        enemy.hp -= cat.atk
                        cat.last_attack_time = now
                        cat.is_attacking = True
                        enemy.is_attacking = True
                        # 記錄接觸點
                        contact_rect = cat_attack_zone.clip(enemy.get_rect())
                        contact_point = contact_rect.center
                        cat.contact_points.append(contact_point)
                        enemy.contact_points.append(contact_point)
                    break
            else:
                cat.move()

    # 敵方攻擊我方
    for enemy in enemies:
        enemy_attack_zone = enemy.get_attack_zone()

        if enemy.is_aoe:
            targets = [c for c in cats if enemy_attack_zone.colliderect(c.get_rect())]
            if targets and now - enemy.last_attack_time > 1000:
                for cat in targets:
                    cat.hp -= enemy.atk
                    cat.is_attacking = True
                    contact_rect = enemy_attack_zone.clip(cat.get_rect())
                    contact_point = contact_rect.center
                    cat.contact_points.append(contact_point)
                    enemy.contact_points.append(contact_point)
                enemy.last_attack_time = now
                enemy.is_attacking = True
            else:
                enemy.move()
        else:
            for cat in cats:
                if enemy_attack_zone.colliderect(cat.get_rect()):
                    if now - enemy.last_attack_time > 1000:
                        cat.hp -= enemy.atk
                        enemy.last_attack_time = now
                        enemy.is_attacking = True
                        cat.is_attacking = True
                        contact_rect = enemy_attack_zone.clip(cat.get_rect())
                        contact_point = contact_rect.center
                        cat.contact_points.append(contact_point)
                        enemy.contact_points.append(contact_point)
                    break
            else:
                enemy.move()

    # 移除死亡單位
    cats[:] = [c for c in cats if c.hp > 0]
    enemies[:] = [e for e in enemies if e.hp > 0]

# === 初始化 ===
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("貓咪大戰爭：攻擊範圍版")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# === 資料 ===

cat_types = {
    "basic":  lambda x, y: Cat(x, y, hp=100, atk=10, speed=1, attack_range=50, is_aoe=False),
    "speedy": lambda x, y: Cat(x, y, hp=70, atk=5, speed=2, attack_range=30, is_aoe=False),
    "tank":   lambda x, y: Cat(x, y, hp=200, atk=15, speed=0.5, attack_range=60, is_aoe=True),
}

cat_cooldowns = {
    "basic": 1000,
    "speedy": 500,
    "tank": 2000,
}

last_spawn_time = {
    "basic": 0,
    "speedy": 0,
    "tank": 0,
}

cat_key_map = {
    pygame.K_1: "basic",
    pygame.K_2: "speedy",
    pygame.K_3: "tank",
}

button_rects = {
    "basic": pygame.Rect(50, 50, 100, 50),
    "speedy": pygame.Rect(200, 50, 100, 50),
    "tank": pygame.Rect(350, 50, 100, 50),
}

button_colors = {
    "normal": (100, 200, 100),
    "cooldown": (180, 180, 180),
}

cats = []
enemies = []

cat_y = 500
enemy_y = 500

enemy_spawn_interval = 3000
last_enemy_spawn_time = 0

# === 主迴圈 ===

running = True
while running:
    screen.fill((255, 255, 255))
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key in cat_key_map:
                cat_type = cat_key_map[event.key]
                if current_time - last_spawn_time[cat_type] >= cat_cooldowns[cat_type]:
                    start_x = 800 - 40
                    cats.append(cat_types[cat_type](start_x, cat_y))
                    last_spawn_time[cat_type] = current_time

    # 自動生成敵人
    if current_time - last_enemy_spawn_time >= enemy_spawn_interval:
        enemies.append(Enemy(0, enemy_y, hp=100, atk=10, speed=1, attack_range=40, is_aoe=False))
        last_enemy_spawn_time = current_time

    # 更新戰鬥邏輯
    update_battle(cats, enemies, current_time)

    # 畫出單位
    for cat in cats:
        cat.draw(screen)
    for enemy in enemies:
        enemy.draw(screen)

    # 畫冷卻按鈕
    for cat_type, rect in button_rects.items():
        time_since = current_time - last_spawn_time[cat_type]
        cooldown = cat_cooldowns[cat_type]
        is_ready = time_since >= cooldown
        color = button_colors["normal"] if is_ready else button_colors["cooldown"]
        pygame.draw.rect(screen, color, rect)
        label = font.render(f"{cat_type} ({list(cat_key_map.keys())[list(cat_key_map.values()).index(cat_type)] - 48})", True, (0, 0, 0))
        screen.blit(label, (rect.x + 5, rect.y + 5))
        if not is_ready:
            ratio = time_since / cooldown
            bar_width = rect.width * (1 - ratio)
            pygame.draw.rect(screen, (255, 100, 100), (rect.x, rect.y + rect.height - 5, bar_width, 5))

    # 畫說明文字
    screen.blit(font.render("按 1,2,3 生產不同貓咪（從右往左攻擊）", True, (0, 0, 0)), (10, 10))
    screen.blit(font.render("紅點為攻擊接觸點", True, (255, 0, 0)), (10, 30))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
