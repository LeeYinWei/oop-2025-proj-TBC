import pygame
import math
import sys, os
import random

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