import pygame
import math
import sys, os
import random

class PhysicEffect:
    def __init__(self, x, y, duration=1000):
        self.x = x
        self.y = y
        self.start_time = pygame.time.get_ticks()
        self.duration = duration  # 煙霧持續時間
        self.alpha = 255
        self.scale = random.uniform(0.1, 0.2)  # 隨機煙霧大小
        self.color = (150, 150, 150)  # 灰色煙霧

        self.frames = []
        for i in range(1, 11, 2):  # 假設有 shockwave0.png ~ shockwave4.png
            img = pygame.image.load(f"physic/physic_{i}.png").convert_alpha()
            if self.scale != 1.0:
                new_size = (int(img.get_width() * self.scale), int(img.get_height() * self.scale))
                img = pygame.transform.scale(img, new_size)
            image_copy = img.copy()
            image_copy.set_alpha(self.alpha)
            self.frames.append(image_copy)

    def update(self):
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time
        if elapsed >= self.duration:
            return False
        #self.alpha = max(0, 1.0 - (elapsed / self.duration))  # 逐漸消失
        #self.size += 0.5  # 煙霧逐漸擴散
        #self.y -= 0  # 向上飄動
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