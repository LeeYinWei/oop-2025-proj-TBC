import pygame
import os

from ..entities import cat_types, cat_costs, cat_cooldowns

_level_selection_background_image = None
_level_selection_background_image_path = "background/level_selection_bg.png"

def load_level_selection_background_image(screen_width, screen_height):
    """
    載入並縮放關卡選擇背景圖片。
    這個函數應該只被調用一次。
    """
    global _level_selection_background_image
    if _level_selection_background_image is None:
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            image_path = os.path.join(base_dir, _level_selection_background_image_path)
            image = pygame.image.load(image_path).convert()
            _level_selection_background_image = pygame.transform.scale(image, (screen_width, screen_height))
        except pygame.error as e:
            print(f"Error loading level selection background image: {e}")
            _level_selection_background_image = None
    return _level_selection_background_image

def draw_level_selection(screen, levels, selected_level, selected_cats, font, completed_levels, cat_images):
    background_image = load_level_selection_background_image(screen.get_width(), screen.get_height())
    if background_image:
        screen.blit(background_image, (0, 0))
    else:
        screen.fill((0, 0, 0))

    title = font.render("Select Level and Cats", True, (255, 255, 255))
    screen.blit(title, (350, 50))
    cat_rects = {}

    for i, level in enumerate(levels):
        rect = pygame.Rect(50, 100 + i * 60, 200, 50)
        is_playable = i == 0 or (i - 1) in completed_levels
        color = (0, 255, 0) if i == selected_level and is_playable else (100, 200, 100) if is_playable else (180, 180, 180)
        pygame.draw.rect(screen, color, rect)
        level_text = font.render(level.name if is_playable else f"{level.name} (Locked)", True, (255, 255, 255))
        screen.blit(level_text, (rect.x + 5, rect.y + 15))

    for idx, cat_type in enumerate(cat_types.keys()):
        rect = pygame.Rect(270 + (idx % 5) * 200, 100 + (idx // 5) * 60, 180, 50)
        cat_rects[cat_type] = rect
        color = (0, 255, 0) if cat_type in selected_cats else (200, 200, 200)
        pygame.draw.rect(screen, color, rect)
        # 畫圖片（下方居中）
        if cat_type in cat_images:
            cat_img = cat_images[cat_type]
            img_x = rect.x + (rect.width - cat_img.get_width()) // 2
            img_y = rect.y + 60
            screen.blit(cat_img, (img_x, img_y))
        screen.blit(font.render(cat_type, True, (255, 255, 255)), (rect.x + 5, rect.y + 15))
        cost = cat_costs.get(cat_type, 0)
        cost_text = font.render(f"Cost: {cost}", True, (255, 255, 255))
        screen.blit(cost_text, (rect.x + 5, rect.y + 30))

    reset_rect = pygame.Rect(50, 400, 200, 50)
    pygame.draw.rect(screen, (255, 100, 100), reset_rect)
    reset_text = font.render("Reset Progress", True, (255, 255, 255))
    screen.blit(reset_text, (reset_rect.x + 40, reset_rect.y + 15))

    quit_rect = pygame.Rect(50, 470, 200, 50)
    pygame.draw.rect(screen, (200, 50, 50), quit_rect)
    quit_text = font.render("Quit", True, (255, 255, 255))
    screen.blit(quit_text, (quit_rect.x + 70, quit_rect.y + 15))

    screen.blit(font.render("Click to select level, click to toggle cats, press Enter to start", True, (255, 255, 255)), (50, 540))

    return cat_rects, reset_rect, quit_rect