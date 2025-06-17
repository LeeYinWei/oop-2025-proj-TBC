import pygame, os

from ..entities.csmokeeffect import CSmokeEffect
from ..entities.tower import Tower

_mission_complete_background_image = None
_mission_complete_background_image_path = "background/mission_complete_bg.jpg"

def load_mission_complete_background_image(screen_width, screen_height):
    """
    載入並縮放首通背景圖片。
    這個函數應該只被調用一次。
    """
    global _mission_complete_background_image
    if _mission_complete_background_image is None:
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            image_path = os.path.join(base_dir, _mission_complete_background_image_path)
            image = pygame.image.load(image_path).convert_alpha()
            _mission_complete_background_image = pygame.transform.scale(image, (screen_width, screen_height))
        except (pygame.error, FileNotFoundError) as e:
            print(f"Error loading mission complete background image: {e}")
            _mission_complete_background_image = None
    return _mission_complete_background_image

def draw_end_screen(screen, current_level, status, end_font, font, our_tower, enemy_tower, start_time):
    # 背景
    screen.blit(current_level.background, (0, 0))

    # 時間差，用於動畫進度（最大1秒內完成）
    elapsed = pygame.time.get_ticks() - start_time
    scale_progress = min(1.0, elapsed / 1500.0)  # 0~1 之間

    # 動畫縮放參數
    base_font_size = 40
    max_font_size = 120
    animated_font_size = int(base_font_size + (max_font_size - base_font_size) * scale_progress)

    # 建立縮放字體物件
    animated_font = pygame.font.SysFont("Arial", animated_font_size)

    if status == "victory":
        enemy_tower.draw_collapse(screen)
        text_surface = animated_font.render("Victory!", True, (0, 255, 100))
        text_rect = text_surface.get_rect(center=(640, 300))  # 螢幕中央
        screen.blit(text_surface, text_rect)
        if scale_progress == 1.0:
            screen.blit(font.render("Press Enter to continue", True, (0, 0, 0)), (460, 400))

    elif status == "lose":
        our_tower.draw_collapse(screen)
        text_surface = animated_font.render("Defeat!", True, (255, 100, 100))
        text_rect = text_surface.get_rect(center=(640, 300))
        screen.blit(text_surface, text_rect)
        if scale_progress == 1.0:
            screen.blit(font.render("Press any key to return to level selection", True, (0, 0, 0)), (460, 400))