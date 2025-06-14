import pygame
import math
import sys, os
import random
# 如果需要使用 BOTTOM_Y
from game.constants import BOTTOM_Y

# 如果需要用 load_config
from game.config_loader import load_config

from game.entities.smokeeffect import SmokeEffect

class Soul:
    def __init__(self, x, y, radius=10, duration=1000):
        self.x = x
        self.y = y
        self.radius = radius
        self.start_time = pygame.time.get_ticks()
        self.duration = duration
        self.alpha = 1.0
        self.color = (255, 255, 255)  # 白色圓形

    def update(self):
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time
        if elapsed >= self.duration:
            return False
        self.y -= 0.5  # 上升動畫
        self.alpha = max(0, 1.0 - (elapsed / self.duration))  # 透明度漸變
        return True

    def draw(self, screen):
        if self.alpha > 0:
            soul_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                soul_surface,
                (self.color[0], self.color[1], self.color[2], int(self.alpha * 255)),
                (self.radius, self.radius),
                self.radius
            )
            screen.blit(soul_surface, (self.x - self.radius, self.y - self.radius))