import pygame
import math
import sys, os
import random

class ShockwaveEffect:
    def __init__(self, x, y, duration=4000, scale=1.0):
        self.x = x
        self.y = y
        self.start_time = pygame.time.get_ticks()
        self.duration = duration
        self.scale = scale
        self.alpha = 1.0

        self.frames = []
        for i in range(1, 11):  # 假設有 shockwave0.png ~ shockwave4.png
            img = pygame.image.load(f"images/effects/shockwave/Explosion_{i}.png").convert_alpha()
            if self.scale != 1.0:
                new_size = (int(img.get_width() * self.scale), int(img.get_height() * self.scale))
                img = pygame.transform.scale(img, new_size)
            self.frames.append(img)

    def update(self, now):
        current_time = now
        elapsed = current_time - self.start_time
        if elapsed >= self.duration:
            # print(f"DEBUG: Shockwave at ({self.x},{self.y}) finished.")
            return False
        self.alpha = max(0, 1.0 - (elapsed / self.duration))
        return True

    def draw(self, screen):
        now = pygame.time.get_ticks()
        elapsed = now - self.start_time
        progress = elapsed / self.duration

        if progress >= 1.0:
            return

        index = int(progress * len(self.frames))
        index = min(index, len(self.frames) - 1)

        image = self.frames[index]
        rect = image.get_rect(center=(self.x, self.y))
        screen.blit(image, rect)