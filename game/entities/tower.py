import pygame
import math
import sys, os
import random

from game.entities.smokeeffect import SmokeEffect
from game.entities.csmokeeffect import CSmokeEffect

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
        self.csmoke_effects = []
        self.shake_duration = 200  # 抖動持續時間（毫秒）
        self.shake_magnitude = 5   # 抖動幅度（像素）
        self.shake_start_time = 0
        self.is_shaking = False
        self.collapsing_start_time = 0
        self.collapsing_magnitude = 8 # 倒塌時的抖動幅度
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
            offset_x = 0
            if self.is_shaking:
                elapsed = pygame.time.get_ticks() - self.shake_start_time
                if elapsed < self.shake_duration:
                    # 根據時間算出左右晃動偏移量（正弦波）
                    offset_x = int(math.sin(elapsed * 0.05) * self.shake_magnitude)
                else:
                    self.is_shaking = False
            # 繪製塔樓圖片，並加上抖動偏移
            
            screen.blit(self.image, (self.x+offset_x, self.y))
    
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
            # 抖動效果
            if not self.is_shaking:
                self.shake_start_time = pygame.time.get_ticks()
                self.is_shaking = True
    

            # 被攻擊時生成煙霧特效，3-5 個粒子，位置在角色中心
            center_x = self.x + self.width // 2
            center_y = self.y + self.height // 2
            for _ in range(random.randint(3, 5)):
                smoke_x = center_x + random.randint(-5, 5)  # 小範圍隨機偏移
                smoke_y = center_y + random.randint(-5, 5)  # 小範圍隨機偏移
                self.smoke_effects.append(SmokeEffect(smoke_x, smoke_y))

    def update_smoke_effects(self):
        self.smoke_effects = [smoke for smoke in self.smoke_effects if smoke.update()]

        
    def draw_collapse(self, screen):
        if self.image:
            elapsed = pygame.time.get_ticks() - self.collapsing_start_time

                    # 根據時間算出左右晃動偏移量（正弦波）
            offset_x = int(math.sin(elapsed * 0.05) * self.collapsing_magnitude)
            # 繪製塔樓圖片，並加上抖動偏移
            
            screen.blit(self.image, (self.x+offset_x, self.y))
    
        else:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        self.draw_hp_bar(screen)
        # 繪製煙霧特效
        for csmoke in self.csmoke_effects:
            csmoke.draw(screen)
            #print("draw csmoke")
        
            
    