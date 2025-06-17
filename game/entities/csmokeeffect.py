import pygame
import math
import sys, os
import random

class CSmokeEffect:
    def __init__(self, x1, y1, x2, y2, frames1, frames2,  duration=1000):
        self.x1 = x1#for type1
        self.y1 = y1
        self.x2 = x2#for type2
        self.y2 = y2
        self.start_time = pygame.time.get_ticks()
        self.duration = duration  # 煙霧持續時間
        self.alpha = 255
        self.scale1 = random.uniform(0.4, 0.5)  # 隨機煙霧大小
        self.scale2 = random.uniform(0.4, 0.6)
        self.color = (150, 150, 150)  # 灰色煙霧

        self.frames1 = frames1
        self.frames2 = frames2

    
        '''
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time
        if elapsed >= self.duration:
            return False
        self.alpha = max(0, 1.0 - (elapsed / self.duration))  # 逐漸消失
        #self.size += 0.5  # 煙霧逐漸擴散
        self.y -= 0.8  # 向上飄動
        return True
        '''

    def draw(self, screen):
        now = pygame.time.get_ticks()
        elapsed = now - self.start_time
        progress = elapsed / self.duration

        progress %= 1.0  # 確保 progress 在 0 到 1 之間

        index = int(progress * len(self.frames1))
        index = min(index, len(self.frames1) - 1)

        image1 = self.frames1[index]
        rect1 = image1.get_rect(center=(self.x1, self.y1))
        screen.blit(image1, rect1)
        image2 = self.frames2[index]
        rect2 = image2.get_rect(center=(self.x2, self.y2))
        screen.blit(image2, rect2)