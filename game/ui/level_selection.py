import pygame
import os

from ..entities import cat_types, cat_costs, cat_cooldowns

_level_selection_background_image = None
_level_selection_background_image_path = "images/background/level_selection_bg.png"

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

def draw_level_selection(screen, levels, selected_level, selected_cats, font, select_font, completed_levels, cat_images, square_surface):
    background_image = load_level_selection_background_image(screen.get_width(), screen.get_height())
    if background_image:
        screen.blit(background_image, (0, 0))
    else:
        screen.fill((0, 0, 0))

    screen.blit(square_surface, (40, 90))  # 將正方形貼上去
    title = select_font.render("Select Level and Cats", True, (0, 0, 0))
    screen.blit(title, (48, 45))
    cat_rects = {}

    for i, level in enumerate(levels):
        rect = pygame.Rect(50, 100 + i * 60, 200, 50)
        is_playable = i == 0 or (i - 1) in completed_levels
        color = (158, 179, 155) if i == selected_level and is_playable else (104, 117, 102) if is_playable else (150, 150, 150)
        pygame.draw.rect(screen, color, rect)
        level_text = font.render(level.name if is_playable else f"{level.name} (Locked)", True, (255, 255, 255))
        screen.blit(level_text, (rect.x + 5, rect.y + 15))

    for idx, cat_type in enumerate(cat_types.keys()):
        rect = pygame.Rect(270 + (idx % 5) * 200, 100 + (idx // 5) * 60, 180, 50)
        cat_rects[cat_type] = rect
        color = (158, 179, 155) if cat_type in selected_cats else (150, 150, 150)
        pygame.draw.rect(screen, color, rect)
        # 畫圖片（下方居中）
        if cat_type in cat_images:
            cat_img = cat_images[cat_type]
            img_x = rect.x + (rect.width - cat_img.get_width()) // 2
            img_y = rect.y + 60
            screen.blit(cat_img, (img_x, img_y))
            # 畫邊框
            border_rect = pygame.Rect(img_x - 2, img_y - 2, cat_img.get_width() + 4, cat_img.get_height() + 4)
            if cat_type in selected_cats:
                pygame.draw.rect(screen, (71, 240, 71), border_rect, 3)  # 綠色框線
        screen.blit(font.render(cat_type, True, (255, 255, 255)), (rect.x + 10, rect.y + 8))
        cost = cat_costs.get(cat_type, 0)
        cost_text = font.render(f"Cost: {cost}", True, (255, 255, 255))
        screen.blit(cost_text, (rect.x + 10, rect.y + 30))

    reset_rect = pygame.Rect(50, 400, 200, 50)
    pygame.draw.rect(screen, (255, 100, 100), reset_rect)
    reset_text = font.render("Reset Progress", True, (255, 255, 255))
    screen.blit(reset_text, (reset_rect.x + 40, reset_rect.y + 15))

    quit_rect = pygame.Rect(50, 470, 200, 50)
    pygame.draw.rect(screen, (200, 50, 50), quit_rect)
    quit_text = font.render("Quit", True, (255, 255, 255))
    screen.blit(quit_text, (quit_rect.x + 70, quit_rect.y + 15))

    # 添加開始按鈕
    start_rect = pygame.Rect(50, 540, 200, 50)
    pygame.draw.rect(screen, (0, 128, 0), start_rect)  # 綠色按鈕
    start_text = font.render("Start", True, (255, 255, 255))
    screen.blit(start_text, (start_rect.x + 70, start_rect.y + 15))

    screen.blit(font.render("Click to select level, click to toggle cats, click Start to begin", True, (255, 255, 255)), (50, 600))

    return cat_rects, reset_rect, quit_rect, start_rect