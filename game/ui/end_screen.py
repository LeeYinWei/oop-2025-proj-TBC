import pygame, os

from ..entities.csmokeeffect import CSmokeEffect
from ..entities.tower import Tower

_mission_complete_background_image = None
_mission_complete_background_image_path = "images/background/mission_complete_bg.jpg"

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

    # 時間差，用於動畫進度（最大1.5秒內完成）
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
        text_rect = text_surface.get_rect(center=(screen.get_width() // 2, 300))  # 螢幕中央水平對齊
        screen.blit(text_surface, text_rect)
        if scale_progress == 1.0:
            # 將 Continue 按鈕移動到螢幕中間
            continue_rect = pygame.Rect(screen.get_width() // 2 - 175, screen.get_height() // 2 + 100, 350, 50)  # 中心點減去寬度一半
            pygame.draw.rect(screen, (0, 255, 0), continue_rect)  # 綠色按鈕
            screen.blit(font.render("Press enter or click to Continue", True, (0, 0, 0)), 
                       (continue_rect.x + 10, continue_rect.y + 10))

    elif status == "lose":
        our_tower.draw_collapse(screen)
        text_surface = animated_font.render("Defeat!", True, (255, 100, 100))
        text_rect = text_surface.get_rect(center=(screen.get_width() // 2, 300))  # 螢幕中央水平對齊
        screen.blit(text_surface, text_rect)
        if scale_progress == 1.0:
            # 將 Continue 按鈕移動到螢幕中間
            continue_rect = pygame.Rect(screen.get_width() // 2 - 175, screen.get_height() // 2 + 100, 350, 50)  # 中心點減去寬度一半
            pygame.draw.rect(screen, (0, 255, 0), continue_rect)  # 綠色按鈕
            screen.blit(font.render("Press enter or click to Continue", True, (0, 0, 0)), 
                       (continue_rect.x + 10, continue_rect.y + 10))

    # 返回 Continue 按鈕矩形
    return continue_rect if scale_progress == 1.0 else None