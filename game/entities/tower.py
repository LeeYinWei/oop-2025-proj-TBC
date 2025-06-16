import pygame
import math
import sys, os
import random

from game.entities.smokeeffect import SmokeEffect

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
        self.smoke_effects = []  # 儲存煙霧特效實例
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
        # 繪製煙霧特效
        for smoke in self.smoke_effects:
            smoke.draw(screen)

    def draw_hp_bar(self, screen):
        bar_width = self.width
        bar_height = 5
        fill = max(0, self.hp / self.max_hp) * bar_width
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y - 10, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 10, fill, bar_height))
        pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y - 10, bar_width, bar_height), 1)

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, int(self.height))
    
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

    def update_smoke_effects(self):
        self.smoke_effects = [smoke for smoke in self.smoke_effects if smoke.update()]
        
    