import pygame
import math
import sys, os
import random

def load_csmoke_images():
    frames1 = []
    frames2 = []
    scale1 = random.uniform(0.4, 0.6)
    scale2 = random.uniform(0.4, 0.6)
    alpha = 255  # 隨機透明度
    for i in range(1, 11, 2):  # 假設有 shockwave0.png ~ shockwave4.png
            img1 = pygame.image.load(f"images/effects/smoke/collapsed_{i}.png").convert_alpha()
            img2 = pygame.image.load(f"images/effects/smoke/collapsed_v2_{i}.png").convert_alpha()
            new_size1 = (int(img1.get_width() * scale1), int(img1.get_height() * scale1))
            new_size2 = (int(img2.get_width() * scale2), int(img2.get_height() * scale2))
            img1 = pygame.transform.scale(img1, new_size1)
            img2 = pygame.transform.scale(img2, new_size2)

            image_copy1 = img1.copy()
            image_copy1.set_alpha(alpha)
            frames1.append(image_copy1)
            image_copy2 = img2.copy()
            image_copy2.set_alpha(alpha)
            frames2.append(image_copy2)
    return frames1, frames2

def load_electric_images():
    frames = []
    alpha = 255
    scale = random.uniform(0.1, 0.2)  # 隨機煙霧大小
    for i in range(1, 11, 2):  # 假設有 shockwave0.png ~ shockwave4.png
            img = pygame.image.load(f"images/effects/electric/electric_{i}.png").convert_alpha()
            if scale != 1.0:
                new_size = (int(img.get_width() * scale), int(img.get_height() * scale))
                img = pygame.transform.scale(img, new_size)
            image_copy = img.copy()
            image_copy.set_alpha(alpha)
            frames.append(image_copy)
    return frames

def load_gas_images():
    frames = []
    alpha = 255
    scale = random.uniform(0.2, 0.3)  # 隨機煙霧大小
    color = (150, 150, 150)  # 灰色煙霧

    for i in range(1, 11, 2):  # 假設有 shockwave0.png ~ shockwave4.png
        img = pygame.image.load(f"images/effects/gas/Explosion_{i}.png").convert_alpha()
        if scale != 1.0:
            new_size = (int(img.get_width() * scale), int(img.get_height() * scale))
            img = pygame.transform.scale(img, new_size)
        image_copy = img.copy()
        image_copy.set_alpha(alpha)
        frames.append(image_copy)

    return frames

def load_physic_images():
    frames = []
    alpha = 255
    scale = random.uniform(0.1, 0.2)  # 隨機煙霧大小
    color = (150, 150, 150)  # 灰色煙霧
    for i in range(1, 11, 2):  # 假設有 shockwave0.png ~ shockwave4.png
            img = pygame.image.load(f"images/effects/physic/physic_{i}.png").convert_alpha()
            if scale != 1.0:
                new_size = (int(img.get_width() * scale), int(img.get_height() * scale))
                img = pygame.transform.scale(img, new_size)
            image_copy = img.copy()
            image_copy.set_alpha(alpha)
            frames.append(image_copy)

    return frames

def load_smoke_images():
    alpha = 100
    scale = random.uniform(0.1, 0.2)  # 隨機煙霧大小
    color = (150, 150, 150)  # 灰色煙霧

    frames = []
    for i in range(1, 25, 5):  # 假設有 shockwave0.png ~ shockwave4.png
        img = pygame.image.load(f"images/effects/smoke/smoke_frames/processed_frame_{i}.png").convert_alpha()
        if scale != 1.0:
            new_size = (int(img.get_width() * scale), int(img.get_height() * scale))
            img = pygame.transform.scale(img, new_size)
        image_copy = img.copy()
        image_copy.set_alpha(alpha)
        frames.append(image_copy)

    return frames