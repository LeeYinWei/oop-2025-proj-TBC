import pygame
import math
import sys, os
import random

class GasEffect:
    def __init__(self, x, y, frames, duration=800):
        self.x = x
        self.y = y
        self.start_time = pygame.time.get_ticks()
        self.duration = duration  # 煙霧持續時間
        self.frames = frames
        
    def update(self):
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time
        if elapsed >= self.duration:
            return False
        #self.alpha = max(0, 1.0 - (elapsed / self.duration))  # 逐漸消失
        #self.size += 0.5  # 煙霧逐漸擴散
        self.y -= 0.5  # 向上飄動
        return True

    def draw(self, screen):
        now = pygame.time.get_ticks()
        #print(f"GasEffect draw called at {now}, start_time: {self.start_time}, duration: {self.duration}")
        elapsed = now - self.start_time
        progress = elapsed / self.duration

        if progress >= 1.0:
            return

        index = int(progress * len(self.frames))
        index = min(index, len(self.frames) - 1)

        image = self.frames[index]
        rect = image.get_rect(center=(self.x, self.y))
        screen.blit(image, rect)