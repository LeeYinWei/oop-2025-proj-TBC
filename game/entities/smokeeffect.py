import pygame
import math
import sys, os
import random

class SmokeEffect:
    def __init__(self, x, y, frames, duration=500):
        self.x = x
        self.y = y
        self.start_time = pygame.time.get_ticks()
        self.duration = duration  # 煙霧持續時間
        self.alpha = 100
        self.scale = random.uniform(0.1, 0.2)  # 隨機煙霧大小
        self.color = (150, 150, 150)  # 灰色煙霧

        self.frames = frames
    
    def update(self):
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time
        if elapsed >= self.duration:
            return False
        self.alpha = max(0, 1.0 - (elapsed / self.duration))  # 逐漸消失
        #self.size += 0.5  # 煙霧逐漸擴散
        self.y -= 0.8  # 向上飄動
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