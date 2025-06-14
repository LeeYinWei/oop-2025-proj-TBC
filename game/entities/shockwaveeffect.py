import pygame
import math
import sys, os
import random

class ShockwaveEffect:
    def __init__(self, x, y, max_radius=200, duration=1000, thickness=5):
        self.x = x
        self.y = y
        self.start_time = pygame.time.get_ticks()
        self.duration = duration
        self.alpha = 1.0
        self.max_radius = max_radius
        self.thickness = thickness  # 中空圓形的邊框厚度

    def update(self):
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time
        if elapsed >= self.duration:
            return False
        self.alpha = max(0, 1.0 - (elapsed / self.duration))
        return True

    def draw(self, screen):
        if self.alpha > 0:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.start_time
            progress = elapsed / self.duration
            radius = int(self.max_radius * progress)
            if radius > self.thickness:  # 確保內徑大於 0
                inner_radius = max(0, radius - self.thickness)
                outer_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(outer_surface, (100, 100, 255, int(self.alpha * 255)), (radius, radius), radius, self.thickness)
                screen.blit(outer_surface, (self.x - radius, self.y - radius))