import pygame
import random

class Cat:
    def __init__(self, x, y, hp, atk, speed, color, cat_img=None, attack_range=50, is_aoe=False):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = hp  # 最大血量
        self.atk = atk
        self.speed = speed
        self.color = color
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
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

        # 畫血條
        self.draw_hp_bar(screen)

        # 畫接觸點 (紅色小圓)
        for pt in self.contact_points:
            pygame.draw.circle(screen, (255, 0, 0), pt, 5)

    def draw_hp_bar(self, screen):
        bar_width = self.width
        bar_height = 5
        fill = max(0, self.hp / self.max_hp) * bar_width
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
        self.max_hp = hp
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
        fill = max(0, self.hp / self.max_hp) * bar_width
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y - 10, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 10, fill, bar_height))

    def get_attack_zone(self):
        # 從左往右，攻擊範圍在右方
        return pygame.Rect(self.x + self.width, self.y, self.attack_range, self.height)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
class Tower:
    def __init__(self, x, y, hp, tower_img=None):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = hp  # 最大血量
        self.last_attack_time = 0
        self.tower_img = pygame.image.load(tower_img) if tower_img else None
        self.width = self.tower_img.get_width() if self.tower_img else 120
        self.height = self.tower_img.get_height() if self.tower_img else 400
        self.is_attacking = False
        self.contact_points = []


    def draw(self, screen):
        if self.tower_img:
            screen.blit(self.tower_img, (self.x, self.y))
        else:
            pygame.draw.rect(screen, (100, 100, 255), (self.x, self.y, self.width, self.height))

        # 畫血條
        self.draw_hp_bar(screen)

        # 畫接觸點 (紅色小圓)
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
    
def update_battle(cats, enemies, now):
    # 先清空接觸點
    for cat in cats:
        cat.is_attacking = False
        cat.contact_points = []
    for enemy in enemies:
        enemy.is_attacking = False
        enemy.contact_points = []
    # 清空塔的接觸點
    our_tower.contact_points = []
    # 我方攻擊敵人
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
                        #tower.is_attacking = True
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
                # 檢查是否有敵人進入攻擊範圍
                for enemy in enemies:
                    if cat_attack_zone.colliderect(enemy.get_rect()):
                        if now - cat.last_attack_time > 1000:
                            enemy.hp -= cat.atk
                            cat.last_attack_time = now
                            cat.is_attacking = True
                            # 記錄接觸點
                            contact_rect = cat_attack_zone.clip(enemy.get_rect())
                            contact_point = contact_rect.center
                            cat.contact_points.append(contact_point)
                            enemy.contact_points.append(contact_point)
                        break
                else:
                    cat.is_attacking = False
                    cat.move()

    # 敵方攻擊我方
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
                        #tower.is_attacking = True
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

    # 移除死亡單位
    cats[:] = [c for c in cats if c.hp > 0]
    enemies[:] = [e for e in enemies if e.hp > 0]

# === 初始化 ===
pygame.init()
screen = pygame.display.set_mode((1000, 600))
pygame.display.set_caption("貓咪大戰爭：攻擊範圍版")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)
# === 遊戲狀態 ===
status = 0#   狀態：0 = 勝負未定，1 = win, 2 = lose

# === 資料 ===

cat_types = {
    "basic":  lambda x, y: Cat(x, y, hp=100, atk=10, speed=1, color = (200, 200, 200), attack_range=50, is_aoe=False),
    "speedy": lambda x, y: Cat(x, y, hp=70, atk=5, speed=2, color = (150, 150, 150),attack_range=30, is_aoe=False),
    "tank":   lambda x, y: Cat(x, y, hp=200, atk=15, speed=0.5, color = (120, 120, 120), attack_range=60, is_aoe=True),
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

our_tower = Tower(850, 140, hp=1000, tower_img=None)
enemy_tower = Tower(20, 140, hp=1000, tower_img=None)

enemy_spawn_interval = 3000
last_enemy_spawn_time = -enemy_spawn_interval
last_budget_increase_time = -1000  # 初始化為負值，確保第一次增加花費時不會有延遲
total_budget_limitation = 1000  # 總花費限制
current_budget = 1000 # 當前餘額
budget_rate = 30  # 每秒增加的花費 

# === 主迴圈 ===

running = True
while running:
    screen.fill((255, 255, 255))
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key in cat_key_map and current_budget >= cat_costs[cat_key_map[event.key]]:
                # 檢查預算是否足夠
                current_budget -= cat_costs[cat_key_map[event.key]]
                # 生成貓咪
                cat_type = cat_key_map[event.key]
                if current_time - last_spawn_time[cat_type] >= cat_cooldowns[cat_type]:
                    start_x = 1000 - 100
                    cats.append(cat_types[cat_type](start_x, cat_y))
                    last_spawn_time[cat_type] = current_time

    # 自動生成敵人
    if current_time - last_enemy_spawn_time >= enemy_spawn_interval:
        enemies.append(Enemy(20, enemy_y, hp=100, atk=10, speed=1, attack_range=40, is_aoe=False))
        last_enemy_spawn_time = current_time

    # 每秒增加預算
    if current_time - last_budget_increase_time >= 1000:
        if current_budget < total_budget_limitation:
            current_budget = min(current_budget+budget_rate, total_budget_limitation)
            last_budget_increase_time = current_time

    # 更新戰鬥邏輯
    update_battle(cats, enemies, current_time)

    # 畫出預算
    budget_text = font.render(f"Current Budget: {current_budget}", True, (0, 0, 0))
    screen.blit(budget_text, (800, 10))

    # 畫出單位
    for cat in cats:
        cat.draw(screen)
    for enemy in enemies:
        enemy.draw(screen)

    # 畫出塔
    our_tower.draw(screen)
    enemy_tower.draw(screen)

    # 畫冷卻按鈕
    for cat_type, rect in button_rects.items():
        time_since = current_time - last_spawn_time[cat_type]
        cooldown = cat_cooldowns[cat_type]
        is_ready = time_since >= cooldown
        color = button_colors["normal"] if is_ready else button_colors["cooldown"]
        pygame.draw.rect(screen, color, rect)
        name_label_text = f"{cat_type} ({list(cat_key_map.keys())[list(cat_key_map.values()).index(cat_type)] - 48})"
        cost_label_text = f"cost: {cat_costs[cat_type]}"
        name_label = font.render(name_label_text, True, (0, 0, 0))
        cost_label = font.render(cost_label_text, True, (255, 0, 0))

        screen.blit(name_label, (rect.x + 5, rect.y + 5))
        screen.blit(cost_label, (rect.x + 5, rect.y + 23))

        if not is_ready:
            ratio = time_since / cooldown
            bar_width = rect.width * (1 - ratio)
            pygame.draw.rect(screen, (255, 100, 100), (rect.x, rect.y + rect.height - 5, bar_width, 5))

    # 畫說明文字
    screen.blit(font.render("Press 1, 2, 3 to produce different cats (attacking from right to left)", True, (0, 0, 0)), (10, 10))
    screen.blit(font.render("Red dots indicate attack contact points", True, (255, 0, 0)), (10, 30))

    pygame.display.flip()

    # 檢查勝負
    if our_tower.hp <= 0:
        status = 2  # lose
        running = False
    elif enemy_tower.hp <= 0:  # 如果沒有敵人了
        status = 1  # win
        running = False
        
    # 限制幀率
    clock.tick(60)

# === 結束畫面 ===
end_font = pygame.font.SysFont(None, 96)  # 指定字體大小為 96 像素
if status == 1:
    screen.blit(end_font.render("You Win!", True, (0, 255, 0)), (350, 200))
elif status == 2:
    screen.blit(end_font.render("You Lose!", True, (255, 0, 0)), (350, 200))

screen.blit(font.render("Press any key to exit", True, (0, 0, 0)), (360, 270))

pygame.display.flip()  # 更新畫面

# 等待玩家按下任意按鍵
waiting = True
while waiting:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # 玩家點擊關閉按鈕
            waiting = False
        elif event.type == pygame.KEYDOWN:  # 玩家按下任意鍵
            waiting = False

pygame.quit()
